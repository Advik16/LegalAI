from fastapi import HTTPException, APIRouter
from models.query_models import QueryInput, QueryResponse, ChunkMetadata, RetrievedChunks
from services.query_engine import chunk_retrieval, llm_response
import logging
import time 
from contextlib import contextmanager, asynccontextmanager
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

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

@router.post("/query", response_model=QueryResponse)
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
        response = llm_response(top_chunk, query_input.question)
        log_step("Response Generated", step_start_4)
        return QueryResponse(query=query_input.question, retrieved_chunks=retrieved_chunk, response = response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
