def get_main_styles():
    return """
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 25%, #dee2e6 50%, #e9ecef 75%, #f8f9fa 100%);
        background-attachment: fixed;
    }
    
    /* Main content area */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2d3748 50%, #1a202c 100%);
        padding: 2rem;
        margin: -2rem -2rem 2rem -2rem;
        text-align: center;
        border-radius: 15px 15px 0 0;
        color: white;
        box-shadow: 0 4px 15px rgba(26, 54, 93, 0.3);
        border-bottom: 3px solid #d4af37;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Chat container with reverse order */
    .chat-container {
        display: flex;
        flex-direction: column-reverse;
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(248, 249, 250, 0.5);
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    /* Message styling */
    .chat-message {
        padding: 1.2rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        animation: fadeIn 0.3s ease-in;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
        color: white;
        margin-left: 3rem;
        border-left: 4px solid #d4af37;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #2d3748;
        margin-right: 3rem;
        border-left: 4px solid #1a365d;
        border: 1px solid #e2e8f0;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #cbd5e0;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1a365d;
        box-shadow: 0 0 0 3px rgba(26, 54, 93, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(26, 54, 93, 0.3);
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(26, 54, 93, 0.4);
        border-color: #d4af37;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(26, 54, 93, 0.05);
        border-right: 2px solid #1a365d;
    }
    
    /* Alert and info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #1a365d;
    }
    
    .stSuccess {
        background: rgba(72, 187, 120, 0.1);
        border-left-color: #48bb78;
    }
    
    .stError {
        background: rgba(245, 101, 101, 0.1);
        border-left-color: #f56565;
    }
    
    .stInfo {
        background: rgba(66, 153, 225, 0.1);
        border-left-color: #4299e1;
    }
    
    /* Welcome section */
    .welcome-section {
        background: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message {
            margin-left: 1rem;
        }
        .ai-message {
            margin-right: 1rem;
        }
        .main-header h1 {
            font-size: 2rem;
        }
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #1a365d;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #2d3748;
    }
    </style>
     """