import streamlit as st
from .config import initialize_session_state
from .styles import get_main_styles
from .components import (
    render_header, render_sidebar, render_chat_input, 
    render_chat_message, render_welcome_section, render_footer
)
from .utils import handle_chat_interaction

def render_main_page():
    """Render the main application page"""
    
    initialize_session_state()
    
    st.markdown(get_main_styles(), unsafe_allow_html=True)
    
    render_header()
    
    render_sidebar()
    
    user_question, ask_button = render_chat_input()
    
    if ask_button and user_question.strip():
        handle_chat_interaction(user_question)
    
    render_chat_section()
    
    render_footer()

def render_chat_section():
    
    if st.session_state.chat_history:
        st.subheader("📋 Case Analysis History")
        st.markdown("*Latest queries appear first*")
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                render_chat_message(message["content"], is_user=True)
            else:
                render_chat_message(message["content"], is_user=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        render_welcome_section()