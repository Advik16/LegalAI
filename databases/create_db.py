import sqlite3

conn = sqlite3.connect("legal_ai.db")
cur = conn.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    email,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT,
    chunk_id TEXT,
    title,
    page_number INTEGER,
    chunk_index INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, chunk_id)
);
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT,
    messages_json TEXT DEFAULT '{}',
    document_id TEXT,
    chunk_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (document_id, chunk_id) REFERENCES documents(document_id, chunk_id)
);
""")

conn.commit()
conn.close()

print("Database created successfully.")
