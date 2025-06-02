from fastapi import HTTPException, APIRouter
from models.query_models import QueryInput, QueryResponse, ChunkMetadata, RetrievedChunks
from services.query_engine import chunk_retrieval, llm_response

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_vector_store(query_input: QueryInput):
    try:
        chunks = chunk_retrieval(query_input.question, k=query_input.top_k)
        if chunks is None:
            raise HTTPException(status_code=500, detail="Chunking returned None")
        retrieved_chunk = [
            RetrievedChunks(
                content = chunk["content"],
                metadata=ChunkMetadata(**chunk["metadata"])
            ) for chunk in chunks
        ]
        top_chunk = chunks[0]["content"]
        response = llm_response(top_chunk, query_input.question)
        return QueryResponse(query=query_input.question, retrieved_chunks=retrieved_chunk, response = response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
