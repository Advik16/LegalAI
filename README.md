# LegalAI

LegalAI is a virtual legal assistant designed to provide general legal information and assist users with their legal inquiries. It leverages advanced natural language processing (NLP) techniques and a semantic search engine to retrieve and process legal documents.

At the moment, this application refers to the Constitution of India to answer any questions asked by the user. More updates on expanded domains and features will come through in phases.

## Features

- **Semantic Search**: Perform semantic searches on the document embeddings to retrieve relevant information.
- **Interactive Chat**: Engage in a conversational interface to ask legal questions and receive responses.
- **Frontend Interface**: A user-friendly web interface for interacting with the system.

---

## Prerequisites

- Python 3.9 or higher
- Node.js and npm (for the frontend)
- SQLite (for the database)

---

## Installation and Setup

### 1. Backend Setup

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

### 2. Frontend Setup

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

1. Ask questions to perform semantic searches and generate responses.
2. Continue the chat by asking follow-up questions. Follow-up questions will be answered using the same chunk that was leveraged for the first interaction.
3. Chat history will be stored in legal_ai.db.

## Notes
1. This project is for educational purposes only and does not provide legal advice.
2. Always consult a licensed attorney for professional legal counsel.

## License
All rights reserved. This repository is published for portfolio demonstration only.


