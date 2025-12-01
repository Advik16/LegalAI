import os
import shutil
import tempfile
from typing import Optional, List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

def chunk_storage(chunks: List[Dict[str, Any]],
    persist_path: str = "faiss_index",
    document_id: Optional[str] = None,
    overwrite: bool = False,):
    if overwrite:
        try:
            if os.path.exists(persist_path):
                shutil.rmtree(persist_path)
        except Exception as e:
            raise RuntimeError(f"Failed to remove existing persist_path {persist_path} : {e}")
    
    docs = [
        Document(
            page_content=chunk["content"],
            metadata={"page_number": chunk["page_number"], "chunk_index": chunk["chunk_index"], "document_id": chunk.get("document_id", document_id)}
        )
        for chunk in chunks
    ]

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if overwrite:
        
        tmp_dir = tempfile.mkdtemp(prefix="faiss_tmp_")
        try:
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(tmp_dir)

            
            if os.path.exists(persist_path):
                shutil.rmtree(persist_path)
            
            os.replace(tmp_dir, persist_path)
        except Exception as e:
            
            if os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                except Exception:
                    pass
            raise RuntimeError(f"Failed to build & swap FAISS index: {e}")

    else:
        
        if os.path.exists(persist_path):
            try:
                vectorstore = FAISS.load_local(persist_path, embeddings)
                vectorstore.add_documents(docs)
                vectorstore.save_local(persist_path)
            except Exception:
                
                tmp_dir = tempfile.mkdtemp(prefix="faiss_tmp_")
                try:
                    new_vs = FAISS.from_documents(docs, embeddings)
                    new_vs.save_local(tmp_dir)
                    if os.path.exists(persist_path):
                        shutil.rmtree(persist_path)
                    os.replace(tmp_dir, persist_path)
                except Exception as e:
                    if os.path.exists(tmp_dir):
                        try:
                            shutil.rmtree(tmp_dir)
                        except Exception:
                            pass
                    raise RuntimeError(f"Failed to append or recreate FAISS index: {e}")
        else:
            
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(persist_path)

    return True