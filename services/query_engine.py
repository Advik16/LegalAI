from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from transformers import pipeline

pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def chunk_retrieval(question: str, index_path: str = 'faiss_index', k: int = 4):

    print("Loading FAISS index from:", index_path)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectors = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    print("FAISS index loaded successfully")
    print(f"Performing semantic search for: '{question}', top_k={k}")

    results = vectors.similarity_search(question, k=k)

    if not results:
        return []

    similar_chunks = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in results
    ]

    return similar_chunks

def llm_response(chunk: str, question: str) -> str:
    prompt = f"You are an expert law consultant who is using the following to answer the given question. Do not generate response based on other sources and only use the chunk provided as the context: {chunk}\n\nQuestion: {question}"
    print("Generating response...")

    result = pipeline(prompt, max_length=200, do_sample=False)

    return result[0]['generated_response']


