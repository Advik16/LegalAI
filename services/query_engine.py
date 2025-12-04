from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from transformers import pipeline
import ollama
import logging
import sqlite3
import json

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#pipeline_model = pipeline("text-generation", model="microsoft/DialoGPT-medium")

def chunk_retrieval(question: str, index_path: str = 'faiss_index', k: int = 1):

    print("Loading FAISS index from:", index_path)
    
    
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

def llm_response(chunk: str, question: str):
    prompt = f"""You are an expert law consultant who is using the following from the constitution to answer the given question. Based on the chunk provided below, answer the question that the user is asking.
    
    Context: {chunk}
    Question: {question}

    
    While generating a response, please consider the following guidelines and guardrails -
    1. You are helping a normal citizen understand the laws, therefore, ensure that you are not using heavy legal terminologies unless user asks you to.
    2. Please mention the source of the information such as Article 15, if the user is asking about a law.
    3. Be conversational with the user based on the tone of the question, at times user may give ask questions to help them understand a critical legal situation, you have to ensure that you understand the tone and synchronize with that.
    4. Do not generate information based on any other source, only use the chunk provided to answer the question. In the event where a chunk is not able to help you answer, simply say I do not know.
    5. Do not re-confirm the question asked by the user.
    6. Ask follow up questions from the user, like do you want more information about this etc.
    7. DO NOT FORM ANY ADDITIONAL POLITICAL OPINION OF YOUR OWN. ENSURE THAT YOU ARE NOT GIVING RESPONSES BASED ON A PARTICULAR SIDE.
    8. Do not mention the source as chunk, instead say according to the sources."""
    
    print("Sending Prompt to LLAMA...")


    for token in ollama.chat(
        model='llama3.2',
        messages=[
            {"role": "system", "content": "You are a helpful and precise law assistant."},
            {"role": "user", "content": prompt}
        ], stream=True
    ):
        content = token.get("message", {}).get("content", "")
        if content:
            logging.debug(f"Streaming token: {content}")
            yield content
    logging.info("Streaming completed successfully.")

def llm_chat_response(conversation_id: str, question: str):
    conn = sqlite3.connect('legal_ai.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT messages_json FROM conversations WHERE conversation_id = ?", (conversation_id,))
        row = cursor.fetchone()
        if row and row[0]:
            raw_messages_json = row[0]
        else:
            raw_messages_json = None
        
        try:
                parsed_messages = json.loads(raw_messages_json)
                messages_json_str = json.dumps(parsed_messages)
        except Exception:
                messages_json_str = str(raw_messages_json) 
            

            
        cursor.execute("""
                        SELECT d.content
                        FROM documents d
                        JOIN conversations c
                        ON c.document_id = d.document_id AND c.chunk_id = d.chunk_id
                        WHERE c.conversation_id = ?
                        """, (conversation_id,))
        result = cursor.fetchone()
        if result and result[0]:
            chunk_content = result[0]
        else:
            return "Error: Chunk content not found"
            
        prompt = f"""You are an expert law consultant continuing a conversation. Based on the previous messages and the chunk provided below, answer the question that the user is asking.
            
            Previous Messages: {messages_json_str}
            Context: {chunk_content}
            Question: {question}

            Please note the following - 
            1. Previous messages has two keys - Content and History. Content is the latest interaction you had with the user and History is the historical chats starting from the earliest.
            2. Context is the information you used to base your answers on.
            3. Question is the user's latest question that you need to answer based on Previous Messages and Context.

            While generating a response, please consider the following guidelines and guardrails -
            1. Continue the chat in a natural manner by ensuring that you are leveraging Previous Messages and Context.
            2. Use all the sources at your disposal but primarily consider the chunk provided.
            3. If the Context does not have the response to the follow-up question, then leverage additional sources at your disposal.
            4. Respond to questions like a legal professional and maintain that tone.
            5. DO NOT REPEAT THE QUESTION IN YOUR RESPONSE AND DO NOT FORM POLITICAL OPINIONS."""

        print("Sending Prompt to LLAMA...")

        
        for token in ollama.chat(
            model = 'llama3.2',
            messages=[
                {"role": "system", "content": "You are a helpful and precise law assistant"},
                {"role": "user", "content": prompt},
            ], stream = True,
        ):
                content = token.get("message", {}).get("content", "")
                if content:
                    logging.debug("Streaming chat token for %s: %s", conversation_id, content)
                    yield content
        logging.info("Streaming completed successfully.")
    finally:
        try:
             cursor.close()
        except Exception:
             pass
        try:
             conn.close()
        except Exception:
             pass  



