from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from transformers import pipeline
import ollama

#pipeline_model = pipeline("text-generation", model="microsoft/DialoGPT-medium")

def chunk_retrieval(question: str, index_path: str = 'faiss_index', k: int = 1):

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
    prompt = f"""You are an expert law consultant who is using the following from the constitution to answer the given question. Do not generate response based on other sources and only use the chunk provided as the context: 
    
    Context: {chunk}
    Question: {question}

    Answer:"""
    print("Sending Prompt to LLAMA...")


    response = ollama.chat(
        model='phi3',
        messages=[
            {"role": "system", "content": "You are a helpful and precise law assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print("Response Generation Complete")

    return response['message']['content']



