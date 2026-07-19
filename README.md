# NovaQuest AI: Multilingual RAG Document QA System

A self-hosted, privacy-first **Retrieval-Augmented Generation (RAG)** platform designed to query and analyze documents (such as resumes, project documentation, or technical manuals) using local embeddings and high-speed open-source language models. 

This project features a high-performance **FastAPI backend**, a modern **React + Vite frontend dashboard**, and a local **ChromaDB vector database**.

---

## 🚀 Key Features

*   **Multilingual Semantic Search:** Uses `paraphrase-multilingual-MiniLM-L12-v2` local embeddings to support queries in **English, Hindi, and Hinglish** (e.g., *"mene internship kiya hai kya?"*) matched against English documents.
*   **Cost-Free Inference:** Powered by **Groq API** (`llama-3.1-8b-instant`) for ultra-fast response times and **HuggingFace** for free, local vector embedding generation (runs entirely on CPU).
*   **High Precision Chunking:** Optimized text splitting (`chunk_size=400`, `chunk_overlap=40`) to prevent context bleed between dense sections (ideal for parsing resumes and technical logs).
*   **Strict Grounding (Anti-Hallucination):** Prompts are constrained to answer questions *only* if the facts exist in the retrieved context. If the data isn't found, the system cleanly states it rather than hallucinating answers.
*   **Persistent Chat History:** Integrated client-side storage (`localStorage`) so your conversations survive browser refreshes or server restarts.
*   **Interactive Dashboard:** A dark-themed React dashboard featuring connection indicators, managed files viewer, and drag-and-drop file upload.

---

## 🛠️ Local Setup and Installation

### Prerequisites
*   Python 3.9 or higher
*   Node.js (v18+) and npm

### Step 1: Set Up API Keys
1. Get a free API Key from the [Groq Console](https://console.groq.com/keys).
2. Create/edit the `.env` file in the root directory and add your key:
    ```env
    GROQ_API_KEY=gsk_your_groq_api_key_here
    CHROMA_PATH=chroma
    DATA_PATH=data
    ```

### Step 2: Start the FastAPI Backend (Terminal 1)
Open a terminal in the project root directory and run:
```bash
# Install backend dependencies
pip install -r requirements.txt

# Start the API server
python api.py
```
*Note: The backend API will start on `http://127.0.0.1:8000`. On first launch, it will download the embedding model (~450MB) locally.*

### Step 3: Start the React Frontend (Terminal 2)
Open a second terminal window, navigate to the `frontend` folder, and run:
```bash
# Enter the frontend folder
cd frontend

# Install Node modules
npm install

# Start the Vite React development server
npm run dev
```
*The React UI will launch on `http://localhost:5173`. Open this URL in your web browser to start chatting!*


