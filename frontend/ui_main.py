import streamlit as st
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.config import setup_page_config
from ui.pages import render_main_page

def main():
    """Main application entry point"""
    
    setup_page_config()
    
    
    render_main_page()

if __name__ == "__main__":
    main()