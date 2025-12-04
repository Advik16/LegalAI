import os
import time
import json
import logging
import pickle
import threading
import asyncio
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, List, Dict, Any
from starlette.concurrency import run_in_threadpool

from fastapi import HTTPException, APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse

import faiss
from sentence_transformers import SentenceTransformer

from models.query_models import QueryInput, QueryResponse, ChunkMetadata, RetrievedChunks, QueryChatInput
from services.query_engine import chunk_retrieval, llm_response, llm_chat_response
from databases.extract_db import get_chunk_row
from databases.update_db import start_new_conversation, update_conversation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level globals (populated at startup or by reload_index)
faiss_index = None
docstore = None
embedding_model = None

# A lock used to avoid read/write races between index rebuilds and query handling
_index_lock = threading.Lock()

# Default paths for persisted index and docstore
DEFAULT_PERSIST_DIR = "faiss_index"
DEFAULT_INDEX_PATH = os.path.join(DEFAULT_PERSIST_DIR, "index.faiss")
DEFAULT_DOCSTORE_PATH = os.path.join(DEFAULT_PERSIST_DIR, "index.pkl")


@asynccontextmanager
async def lifespan(app):

    global faiss_index, docstore, embedding_model

    logger.info("Loading FAISS Index and Docstore at startup")

    index_path = DEFAULT_INDEX_PATH
    docstore_path = DEFAULT_DOCSTORE_PATH

    # If index exists, load it; else leave globals None and rely on on-demand creation.
    if os.path.exists(index_path) and os.path.exists(docstore_path):
        with _index_lock:
            faiss_index = faiss.read_index(index_path)
            with open(docstore_path, "rb") as f:
                docstore = pickle.load(f)
        logger.info("Loaded existing FAISS index and docstore.")
    else:
        logger.info("FAISS index or docstore not found at startup; will be created on demand.")

    # Load embedding model (SentenceTransformer) for any local embedding needs
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Embedding model loaded successfully.")

    yield

    logger.info("Shutting down")


def reload_index(index_path: Optional[str] = None, docstore_path: Optional[str] = None) -> None:

    global faiss_index, docstore

    index_path = index_path or DEFAULT_INDEX_PATH
    docstore_path = docstore_path or DEFAULT_DOCSTORE_PATH

    with _index_lock:
        if not os.path.exists(index_path) or not os.path.exists(docstore_path):
            raise RuntimeError(f"Index files not found for reload: {index_path}, {docstore_path}")

        # Read FAISS index and pickle docstore
        faiss_index = faiss.read_index(index_path)

        with open(docstore_path, "rb") as f:
            docstore = pickle.load(f)

        logger.info("FAISS index and docstore reloaded into memory.")


@contextmanager
def log_step(message: str, step_start: float):
    """
    Context manager style helper used to log step timings in functions.
    Usage in code: step_start = time.perf_counter(); <do work>; log_step("Description", step_start)
    """
    elapsed = time.perf_counter() - step_start
    logger.info(f"{message} - Time taken: {elapsed:.4f} seconds")
    try:
        yield
    finally:
        pass


@router.post("/query/stream")
async def query_vector_store_stream(query_input: QueryInput, background_tasks: BackgroundTasks):
    """
    Streaming variant of the query endpoint with slightly different token generator semantics.
    """
    request_start = time.perf_counter()
    logger.info("=" * 60)
    logger.info(f"New streaming query request: '{query_input.question}'")

    try:
        step_start_1 = time.perf_counter()
        chunks = chunk_retrieval(query_input.question, k=query_input.top_k)
        log_step("Chunks retrieved from chunk_retrieval", step_start_1)

        if chunks is None:
            logger.error("Chunks Error Occurred")
            raise HTTPException(status_code=500, detail="Chunking returned None")

        step_start_2 = time.perf_counter()
        retrieved_chunk = [
            RetrievedChunks(
                content=chunk["content"],
                metadata=ChunkMetadata(**chunk["metadata"])
            )
            for chunk in chunks
        ]
        log_step("Retrieved Chunks Processed", step_start_2)

        step_start_3 = time.perf_counter()
        top_chunk = chunks[0]["content"]
        top_meta = ChunkMetadata(**(chunks[0].get("metadata") or {}))
        log_step("Top Chunk Processed", step_start_3)

        step_start_4 = time.perf_counter()

        async def token_generator(top_chunk_local, top_meta_local, query_input_local):
            accumulated_tokens = []
            
            try:
                try:
                    yield f"data: {json.dumps({'source': top_meta_local.dict()})}\n\n"
                except Exception:
                    pass

                for token in llm_response(top_chunk_local, query_input_local.question):
                    accumulated_tokens.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0)
                
                full_response = "".join(accumulated_tokens)

                doc_id = getattr(top_meta_local, "document_id", None)
                page_no = getattr(top_meta_local, "page_number", None)
                chunk_idx = getattr(top_meta_local, "chunk_index", None)

                if doc_id is None or page_no is None or chunk_idx is None:
                    logger.error("Top chunk metadata missing required fields")
                    raise HTTPException(status_code=500, detail="Missing chunk metadata (document_id/page_number/chunk_index)")
                
                chunk_row = await run_in_threadpool(get_chunk_row, doc_id, int(page_no), int(chunk_idx))
                
                if not chunk_row:
                    logger.error("No entry found in documents table for provided metadata")
                    raise HTTPException(status_code=500, detail="No matching chunk row in documents table")
                
                chunk_id = chunk_row["chunk_id"]
                document_id = chunk_row["document_id"]

                #background_tasks.add_task(start_new_conversation, document_id, chunk_id, query_input_local.question, full_response)
                try:
                    conversation_id = await run_in_threadpool(start_new_conversation
                                                              , document_id
                                                              , chunk_id
                                                              , query_input_local.question
                                                              , full_response)
                except Exception as db_exc:
                    logger.exception("start_new_conversation failed")
                    conversation_id = None

                final_event = {
                    "final_response": full_response,
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "conversation_id": conversation_id
                }
                yield f"data: {json.dumps(final_event)}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                yield "data: [DONE]\n\n"

        log_step("Streaming Response Started", step_start_4)

        return StreamingResponse(token_generator(top_chunk, top_meta, query_input), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Query stream failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chat/stream")
async def chat_stream(query_input: QueryChatInput, background_tasks: BackgroundTasks):
    conversation_id = getattr(query_input, "conversation_id", None)
    question = getattr(query_input, "question", None)

    if not conversation_id or not isinstance(conversation_id, str):
        raise HTTPException(status_code=400, detail="conversation_id (str) is required")
    if not question or not isinstance(question, str):
        raise HTTPException(status_code=400, detail="question (str) is required")
    
    logger.info("Starting chat_stream for conversation_id=%s", conversation_id)

    async def token_generator(conv_id: str, q: str):
        accumulated = []

        try:
            for token in llm_chat_response(conv_id, q):
                if isinstance(token, str) and token.startswith("Error:"):
                    yield f"data : {json.dumps({'error': token})}\n\n"
                    break

                try:
                    yield f"data: {json.dumps({'token': token})}\n\n"
                except Exception:
                    yield f"data: {json.dumps({'token': str(token)})}\n\n"

                accumulated.append(str(token))
                time.sleep(0)

            full_response = "".join(accumulated)

            try:
                background_tasks.add_task(update_conversation, conv_id, q, full_response)
            except Exception as e:
                    logger.exception("Failed to schedule update_conversation for %s: %s", conv_id, e)

            final_event = {"final_response": full_response, "conversation_id": conv_id}
            yield f"data: {json.dumps(final_event)}\n\n"

        except Exception as e:
            logger.exception("chat_stream token_generator error for %s: %s", conv_id, e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(token_generator(conversation_id, question), media_type="text/event-stream")
        