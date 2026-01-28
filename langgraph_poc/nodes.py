import ollama
from settings import OLLAMA_MODEL

def ollama_chat(messages):
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages
    )
    return response["message"]["content"]


from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from settings import FAISS_INDEX_PATH, TOP_K

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    FAISS_INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)

from state import RAGState

def retrieve_node(state: RAGState):
    docs = retriever.invoke(state["question"])
    state["retrieved_docs"] = [doc.page_content for doc in docs]
    return state

def answer_node(state: RAGState):
    context = "\n\n".join(state["retrieved_docs"])

    messages = state["messages"] + [
        {
            "role": "user",
            "content": f"""
Use the context below to answer the question.

Context:
{context}

Question:
{state['question']}
"""
        }
    ]

    answer = ollama_chat(messages)

    state["answer"] = answer
    state["messages"].append(
        {"role": "assistant", "content": answer}
    )

    return state

