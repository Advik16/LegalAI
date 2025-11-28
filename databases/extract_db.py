import sqlite3
from typing import Optional, Dict

DB_PATH = "legal_ai.db"


def get_chunk_row(document_id: str, page_number: int, chunk_index: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
         SELECT chunk_id, document_id FROM documents
         WHERE document_id = ? AND page_number = ? AND chunk_index = ?
         LIMIT 1
         """, (document_id, page_number, chunk_index),
        )
        row = cur.fetchone()
        if not row:
            return None
        chunk_id, doc_id = row

        return {"chunk_id": chunk_id, "document_id": doc_id}
    finally:
        conn.close()
