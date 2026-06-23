# 🚀 NovaQuest AI

A production-ready **Retrieval-Augmented Generation (RAG)** application built with LangChain, persistent ChromaDB, and OpenAI. It features a high-speed FastAPI backend and a gorgeous modern React dashboard.

---

## 🛠️ Tech Stack & Features

* **LLM Engine:** OpenAI (`gpt-4o-mini` model for high-speed, contextual synthesis)
* **Embedding Model:** OpenAI (`text-embedding-3-small`)
* **Vector Store:** ChromaDB (persistent SQLite-backed local vector store)
* **Backend:** FastAPI (Python REST API)
* **Frontend:** React + Vite (Vibrant custom dark/neon interface)
* **Features:** Upload multiple files, delete single files, wipe vector space, automated deduplication, and structured citations.

---

## 📂 Project Structure

```text
├── data/                      # Place your source PDFs/TXTs/MDs here
├── chroma/                    # SQLite persistent ChromaDB vector store
├── frontend/                  # React + Vite frontend application
├── api.py                     # FastAPI backend server
├── get_embedding_function.py  # Utility to retrieve OpenAI embeddings
├── populate_database.py       # Data loader & embedding ingestion script
├── query_data.py              # CLI query interface
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration API keys
└── README.md                  # This setup guide
```

---

## 🚀 How to Run the Project

### Step 1: Set Up Your OpenAI API Key
1. Get an API key from [OpenAI Platform](https://platform.openai.com/).
2. Open the `.env` file in the root directory and add your key:
   ```env
   OPENAI_API_KEY=sk-proj-YourOpenAiKeyHere
   ```

### Step 2: Start the FastAPI Backend (Terminal 1)
Open a terminal in the root folder and run:
```bash
# Install Python backend dependencies
pip install fastapi uvicorn python-multipart langchain-openai

# Start the API server
python api.py
```
*The backend API will run on `http://127.0.0.1:8000`.*

### Step 3: Start the React Frontend (Terminal 2)
Open a new terminal window, navigate to the `frontend` directory, and run:
```bash
# Enter the frontend folder
cd frontend

# Install Node modules (if running for the first time)
npm install

# Start the Vite React development server
npm run dev
```
*The React UI will run on `http://localhost:5173`. Open this URL in your browser to use NovaQuest AI!*

---

## 🧪 CLI Querying & Testing
You can still query the system without the frontend by using the CLI tool:
```bash
python query_data.py "Ask your question here"
```
