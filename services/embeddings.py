from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

def chunk_storage(chunks:list, persist_path: str = "faiss_index"):
    docs = [
        Document(
            page_content=chunk["content"],
            metadata={"page_number": chunk["page_number"], "chunk_index": chunk["chunk_index"]}
        )
        for chunk in chunks
    ]

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(persist_path)

    return True