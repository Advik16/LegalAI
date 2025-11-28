from pydantic import BaseModel
from typing import List, Optional

class QueryInput(BaseModel):
    question: str
    top_k: int = 1

class ChunkMetadata(BaseModel):
    page_number: Optional[int]
    chunk_index: Optional[int]
    document_id: str

class RetrievedChunks(BaseModel):
    content: str
    metadata: ChunkMetadata

class QueryResponse(BaseModel):
    query: str
    retrieved_chunks: List[RetrievedChunks]
    response: str

class QueryChatInput(BaseModel):
    question: str
    conversation_id: str
