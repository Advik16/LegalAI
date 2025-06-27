import streamlit as st
from services.api import query_agent

def handle_chat_interaction(user_question):

    st.session_state.chat_history.insert(0, {
        "role": "user", 
        "content": user_question
    })
    
    with st.spinner("🔍 Analyzing legal sources..."):
        response = query_agent(user_question, st.session_state.api_url)
    
    if response:
        ai_response = parse_api_response(response)
    else:
        ai_response = "⚠️ I apologize, but I encountered an error while analyzing your legal query. Please verify the service connection and try again."
    

    st.session_state.chat_history.insert(0, {
        "role": "assistant", 
        "content": ai_response
    })
    
    st.rerun()

def parse_api_response(response):

    if isinstance(response, dict):
        if 'answer' in response:
            return response['answer']
        elif 'response' in response:
            return response['response']
        elif 'result' in response:
            return response['result']
        else:
            return str(response)
    else:
        return str(response)

def format_error_message(error_type, details=""):

    error_messages = {
        "connection": "⚖️ Connection Error: Unable to connect to the Legal AI service",
        "timeout": "⏳ Timeout Error: Legal analysis request took too long",
        "http": "📋 HTTP Error: Please check the legal service status",
        "general": "⚠️ Error occurred during legal analysis"
    }
    
    base_message = error_messages.get(error_type, error_messages["general"])
    return f"{base_message}. {details}" if details else base_message