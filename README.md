# LegalAI

> ⚠️ This is a personal portfolio project published for demonstration and evaluation purposes only.

LegalAI is a virtual legal assistant designed to demonstrate the implementation of a Retrieval-Augmented Generation (RAG) system for legal documents. The application uses semantic search and natural language processing techniques to retrieve relevant legal context and generate informative responses to user queries.

At its current stage, the system is configured to reference the **Constitution of India** as its primary knowledge source. Support for additional legal domains and enhanced features is planned in future phases.

## Features

- **Semantic Search**: Perform semantic searches on the document embeddings to retrieve relevant information.
- **Interactive Chat**: Engage in a conversational interface to ask legal questions and receive responses.
- **Frontend Interface**: A user-friendly web interface for interacting with the system.

---

## Tech Stack

- **Backend:** Python, FastAPI  
- **Vector Search:** FAISS  
- **NLP / Embeddings:** HuggingFace Transformers  
- **Database:** SQLite  
- **Frontend:** Node.js, React

---

## High-Level Architecture

The system ingests legal documents, chunks and embeds the content using transformer-based embeddings, and stores them in a vector index. During user queries, the most relevant chunks are retrieved using semantic similarity search and passed to a locally hosted language model to generate context-aware responses.

---

## Prerequisites

- Python 3.9 or higher
- Node.js and npm (for the frontend)
- SQLite (for the database)
- Ollama (for running llama3.2 locally)

---

## Installation and Setup

### 1. LLM Setup (Ollama)

1. Install Ollama:
https://ollama.com

After installation, verify:
   ```bash
   ollama --version

2. Pull the LLaMa 3.2 Model:
```bash
ollama pull llama3.2

3. Start the Ollama Service:
```bash
ollama serve

### 2. Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. Create a virtual environment:
    ```bash
    python -m venv .venv

3. Activate the virtual environment:
- On Windows:
   ```bash
   .venv\Scripts\activate

- On macOS/Linux:
   ```bash
   source .venv/bin/activate

4. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt

5. Start the backend server using Uvicorn:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8080 --reload

### 3. Frontend Setup

1. Open a new terminal and navigate to legal-ai-frontend folder:
   ```bash
   cd legal-ai-frontend

2. Install the frontend dependencies:
   ```bash
   npm install

3. Start the frontend development server:
   ```bash
   npm run dev

4. Open your browser and navigate to:
   ```bash
   http://localhost:5173

## Usage

1. Ask legal questions to retrieve relevant sections from the document corpus.
2. Continue the conversation with follow-up questions; responses will reference the same retrieved context for consistency.
3. Chat history is persisted locally in legal_ai.db.

## Notes & Disclaimer
This project is intended for educational and demonstration purposes only and does
not provide legal advice.

Always consult a licensed attorney for professional legal counsel.

## License
All rights reserved. This repository is published for portfolio demonstration only.


