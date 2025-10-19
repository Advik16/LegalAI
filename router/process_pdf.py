from fastapi import HTTPException, APIRouter
from services.pdf_parser import pdf_extraction
from services.chunking import chunk_extracted_text
from services.embeddings import chunk_storage
import os

router = APIRouter()

pdf_path = "source_docs/Consitution of India.pdf"

@router.get("/process-pdf")
async def process_local_pdf():
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")

    pages = pdf_extraction(pdf_path)
    chunks = chunk_extracted_text(pages)
    chunk_storage(chunks)

    return {
        "message": "PDF parsed, chunked, and stored in FAISS successfully.",
        "chunks": chunks
    }