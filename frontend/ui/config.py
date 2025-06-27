import streamlit as st

def setup_page_config():

    st.set_page_config(
        page_title = "Legal AI Assistant",
        page_icon = "⚖️",
        layout="wide",
        initial_sidebar_state="auto"
    )

def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_url' not in st.session_state:
        st.session_state.api_url = "http://127.0.0.1:8080/query"
    if 'service_status' not in st.session_state:
        st.session_state.service_status = "unknown"

class AppConstants:
    DEFAULT_API_URL = "http://127.0.0.1:8080/query"
    APP_TITLE = "Legal AI Assistant"
    APP_DESCRIPTION = "Professional Legal Assistant"
    VERSION = "1.0.0"

    LEGAL_SYMBOLS = {
        'main': '⚖️',
        'config': '🏛️',
        'search': '🔍',
        'analysis': '📚',
        'client': '👤',
        'case': '📋',
        'warning': '⚠️',
        'success': '✅',
        'error': '❌'
    }