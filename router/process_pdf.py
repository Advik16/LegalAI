from fastapi import HTTPException, APIRouter, UploadFile, File, Form
from services.pdf_parser import pdf_extraction
from services.chunking import chunk_extracted_text
from services.embeddings import chunk_storage
from databases.update_db import create_document_id, insert_chunks, delete_chunks_by_document_id, get_all_chunks
import tempfile
import os
from datetime import datetime
from router.query_router import reload_index
from typing import Optional

router = APIRouter()

#pdf_path = "source_docs/Consitution of India.pdf"

@router.post("/process-pdf")
async def process_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_id: Optional[str] = Form(None),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please Upload PDF")
    
    tmp_path = None

    try:
        suffix = os.path.splitext(file.filename)[1] or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            contents = await file.read()
            tmp.write(contents)

        pages = pdf_extraction(tmp_path)
        chunks = chunk_extracted_text(pages)
        
        if document_id:
            delete_chunks_by_document_id(document_id)
            insert_count = insert_chunks(document_id=document_id, title=title, chunks=chunks)
            
            all_chunks = get_all_chunks()
            chunk_storage(all_chunks, persist_path = "faiss_index", document_id=None, overwrite=True)
            reload_index()

            return {
                "message": "Existing document overwritten, chunked, and stored in DB and FAISS successfully.",
                "document_id": document_id,
                 "title": title,
                "chunks_count": insert_count
            }
        
        new_doc_id = create_document_id()
        insert_count = insert_chunks(document_id=new_doc_id, title=title, chunks=chunks)
        chunk_storage(chunks, persist_path="faiss_index", document_id=new_doc_id, overwrite=False)
        reload_index()
        return {
                "message": "PDF parsed, chunked, and stored in DB and FAISS successfully.",
                "document_id": document_id,
                 "title": title,
                "chunks_count": insert_count
            }
    except Exception as e:
        raise HTTPException(status_code = 500, detail=str(e))
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass