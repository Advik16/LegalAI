import sqlite3
import uuid
from typing import List, Dict, Any
from datetime import datetime
import json

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

def start_new_conversation(document_id: str, chunk_id: str, user_query: str, llm_response: str):
    conn = _get_conn()
    conversation_id = uuid.uuid4().hex
    user_id = "abc"
    messages_json = {
        "Content": {
            "Query": user_query,
            "Response": llm_response
        },
        "History": []
    }
    created_at = updated_at = datetime.now()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversations (conversation_id, user_id, document_id, chunk_id, messages_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                user_id,
                document_id,
                chunk_id,
                json.dumps(messages_json),
                created_at,
                updated_at,
            ),
        )
        conn.commit()
        return conversation_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_conversation(conversation_id: str, user_query: str, llm_response: str):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT messages_json FROM conversations WHERE conversation_id = ?",
            (conversation_id,),
        )
        row = cur.fetchone()
        if row is None:
            cur.execute("ROLLBACK")
            raise ValueError(F"No conversation found for conversation_id={conversation_id}")
        
        messages = json.loads(row[0])

        old_content = messages["Content"]
        messages["History"].append(old_content)

        messages["Content"] = {
            "Query": user_query,
            "Response": llm_response
        }

        updated_at = datetime.now()

        cur.execute(
            """
          UPDATE conversations
          SET messages_json = ?, updated_at = ?
          WHERE conversation_id = ?
            """,
            (json.dumps(messages), updated_at, conversation_id),
        )
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        cur.close()
        conn.close()