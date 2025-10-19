from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from models.query_models import QueryInput, QueryResponse, ChunkMetadata, RetrievedChunks
from services.query_engine import chunk_retrieval, llm_response
import logging
import time 
from contextlib import contextmanager, asynccontextmanager
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
import json
import asyncio 

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

faiss_index = None
docstore = None
embedding_model =  None

@asynccontextmanager
async def lifespan(app):
    global faiss_index, docstore, embedding_model

    print("Loading FAISS Index and Docstore at startup")

    index_path = os.path.join("faiss_index", "index.faiss")
    docstore_path = os.path.join("faiss_index", "index.pkl")

    faiss_index = faiss.read_index(index_path)

    with open(docstore_path, "rb") as f:
        docstore = pickle.load(f)

    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("FAISS + Docstore + Embedding model Loaded Successfully")

    yield

    print("Shutting down")


@contextmanager
def log_step(message: str, step_start: float):
    elapsed = time.perf_counter() - step_start
    logger.info(f"{message} - Time taken: {elapsed:.4f} seconds")

@router.post("/query") #Old Endpoint
async def query_vector_store(query_input: QueryInput):
    request_start = time.perf_counter()
    logger.info("=" * 60)
    logger.info(f"New query request: '{query_input.question}'")
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
                content = chunk["content"],
                metadata=ChunkMetadata(**chunk["metadata"])
            ) for chunk in chunks
        ]
        log_step("Retrieved Chunks Processed", step_start_2)
        step_start_3 = time.perf_counter()
        top_chunk = chunks[0]["content"]
        log_step("Top Chunk Processed", step_start_3)
        step_start_4 = time.perf_counter()
        def response_generator():
            yield f"data: {json.dumps({'retrieved_chunks': [chunk.model_dump() for chunk in retrieved_chunk]})}\n\n"

            for token in llm_response(top_chunk, query_input.question):
                if token.strip():  
                    yield f"data: {json.dumps({'token': token})}\n\n"

            
            yield "data: [DONE]\n\n"

        log_step("Streaming Response Generated", step_start_4)

        return StreamingResponse(response_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.exception("Error occurred during query processing")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        total_elapsed = time.perf_counter() - request_start
        logger.info(f"Total request time: {total_elapsed:.2f}s")
        logger.info("=" * 60)
    
@router.post("/query/stream")
async def query_vector_store_stream(query_input: QueryInput):
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
        log_step("Top Chunk Processed", step_start_3)

        
        step_start_4 = time.perf_counter()

        def token_generator(top_chunk, query_input):
            try:
                for token in llm_response(top_chunk, query_input.question):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    time.sleep(0)
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                yield "data: [DONE]\n\n"
                
            

        log_step("Streaming Response Started", step_start_4)

        return StreamingResponse(token_generator(top_chunk, query_input), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Query stream failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

