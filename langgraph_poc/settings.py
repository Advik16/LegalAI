from pathlib import Path

# Project root = one level above langgraph_poc
PROJECT_ROOT = Path(__file__).resolve().parent.parent

FAISS_INDEX_PATH = PROJECT_ROOT / "faiss_index"

OLLAMA_MODEL = "llama3.2"
TOP_K = 4
