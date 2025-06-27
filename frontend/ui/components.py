import streamlit as st
from .config import AppConstants

def render_header():
    st.markdown(f"""
    <div class="main-header">
        <h1>{AppConstants.LEGAL_SYMBOLS['main']} {AppConstants.APP_TITLE}</h1>
        <p>{AppConstants.LEGAL_SYMBOLS['analysis']} {AppConstants.APP_DESCRIPTION}</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.header(f"{AppConstants.LEGAL_SYMBOLS['config']} Configuration")

        api_url = st.text_input(
            "Legal Service Endpoint", value=st.session_state.api_url, help="Legal AI service API Endpoint"
        )

        st.session_state.api_url = api_url

        if st.button(f"{AppConstants.LEGAL_SYMBOLS['search']} Test Legal Service"):
            from services.api import test_connection
            if test_connection(api_url):
                st.success(f"{AppConstants.LEGAL_SYMBOLS['search']} Legal service is online")
            else:
                st.error(f"{AppConstants.LEGAL_SYMBOLS['error']} Legal service unavailable")
                st.session_state.service_status = "offline"

        st.divider()

        if st.button(f"{AppConstants.LEGAL_SYMBOLS['case']} Clear Case History"):
            st.session_state.chat_history = []
            st.rerun()

        st.divider()

        render_legal_disclaimer()

def render_legal_disclaimer():
    st.markdown(f"""
    **{AppConstants.LEGAL_SYMBOLS['warning']} Legal Disclaimer**
    
    This AI assistant provides general legal information only. 
    
    {AppConstants.LEGAL_SYMBOLS['case']} Not a substitute for professional legal advice
    
    👨‍💼 Consult qualified legal counsel for specific matters
    """)

def render_chat_input():
    st.header("💼 Legal Query Interface")
    col1, col2 = st.columns([4,1])

    with col1:
        user_question = st.text_input(
            f"{AppConstants.LEGAL_SYMBOLS['search']} Your Legal Question:",
            placeholder="Ask about articles, acts, regulations ...",
            key="question_input"
        )

    with col2:
        st.write("")
        ask_button = st.button(f"{AppConstants.LEGAL_SYMBOLS['main']} Analyze", use_container_width=True)

    return user_question, ask_button

def render_chat_message(message, is_user=True):
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>{AppConstants.LEGAL_SYMBOLS['client']} Client Query:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message ai-message">
            <strong>{AppConstants.LEGAL_SYMBOLS['main']} Legal Analysis:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def render_welcome_section():
    st.markdown("""
        <div class="welcome-section">
            <h3>🏛️ Welcome to your Legal AI Assistant!</h3>
            <p>I'm here to help you research legal matters, analyze cases, and provide insights from legal databases.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📚 Example Legal Queries:")

    with st.container():
        st.markdown("""
                    
                    **Constitutional Law**: What are a citizen's fundamental rights?

                    **Contract Law:** "Explain the elements of a valid contract"

                    **Criminal Law:** "What constitutes probable cause for search and seizure?"

                    """)
        
        st.info("💡 **Tip:** Be specific with your legal questions for more precise analysis")

def render_footer():
    st.divider()
    st.markdown(f"""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        <p>{AppConstants.LEGAL_SYMBOLS['main']} <strong>{AppConstants.APP_TITLE}</strong> • Built with Streamlit</p>
        <p style="font-size: 0.9rem;">{AppConstants.LEGAL_SYMBOLS['case']} Remember: This tool provides information, not legal advice</p>
    </div>
    """, unsafe_allow_html=True)