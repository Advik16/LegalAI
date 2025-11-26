import sqlite3
import uuid
from typing import List, Dict, Any

DB_PATH = "legal_ai.db"

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_document_id() -> str:
    return uuid.uuid4().hex

def delete_chunks_by_document_id(document_id: str) -> int:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()

def insert_chunks(document_id: str, title: str, chunks: List[Dict[str,Any]]) -> int:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        inserted = 0
        for chunk in chunks:
            chunk_id = uuid.uuid4().hex
            page_number = chunk.get("page_number")
            chunk_index = chunk.get("chunk_index")
            content = chunk.get("content", "")

            cur.execute(
                 """INSERT INTO documents (document_id, chunk_id, title, page_number, chunk_index, content)
                VALUES (?, ?, ?, ?, ?, ? )""",
                (document_id, chunk_id, title, page_number, chunk_index, content)
            )
            inserted += 1
    
        conn.commit()
        return inserted
    finally:
        conn.close()

def get_all_chunks() -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT document_id, page_number, chunk_index, content FROM documents ORDER BY document_id, page_number, chunk_index"
        )
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append(
                {
                    "content": r["content"],
                    "page_number": r["page_number"],
                    "chunk_index": r["chunk_index"],
                    "document_id": r["document_id"],
                }
            )
        return result
    finally:
        conn.close()

def create_user_id() -> str:
    return uuid.uuid4().hex
def create_conversation_id() -> str:
    return uuid.uuid4().hex