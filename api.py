import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import LangChain / RAG utilities
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from get_embedding_function import get_embedding_function
from populate_database import split_documents, add_to_chroma

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma"
DATA_PATH = "data"

# Initialize FastAPI app
app = FastAPI(title="NovaQuest AI API", description="FastAPI Backend for NovaQuest AI - Zero-G Knowledge Engine (OpenAI Powered)")

# Add CORS middleware to support local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request/response bodies
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

# Ensure folders exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)


def get_db_stats_helper():
    """Helper to retrieve statistics about the active Chroma index."""
    try:
        if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
            return 0, []
        
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        db_data = db.get(include=["metadatas"])
        
        chunk_count = len(db_data["ids"])
        
        # Extract unique document names from metadata
        sources = set()
        if db_data["metadatas"]:
            for meta in db_data["metadatas"]:
                if meta and "source" in meta:
                    sources.add(os.path.basename(meta["source"]))
                    
        return chunk_count, sorted(list(sources))
    except Exception as e:
        print(f"Error getting DB stats: {e}")
        return 0, []


@app.get("/api/stats")
async def get_stats():
    """Retrieve active database statistics."""
    openai_key = os.getenv("OPENAI_API_KEY")
    has_api_key = bool(openai_key and openai_key != "your_openai_api_key_here")
    chunk_count, doc_list = get_db_stats_helper()
    return {
        "connected": True,
        "has_api_key": has_api_key,
        "chunk_count": chunk_count,
        "documents": doc_list
    }


@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload documents and instantly parse, chunk, and index them into ChromaDB."""
    openai_key = os.getenv("OPENAI_API_KEY")
    has_api_key = bool(openai_key and openai_key != "your_openai_api_key_here")
    if not has_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY environment variable is missing or placeholder.")

    try:
        _, doc_list = get_db_stats_helper()
        new_files_to_ingest = []

        # Save files to disk
        for file in files:
            file_path = os.path.join(DATA_PATH, file.filename)
            
            # Avoid redundant ingestion if file already in database
            if file.filename not in doc_list:
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                new_files_to_ingest.append(file.filename)
        
        # Ingest new files if any
        if new_files_to_ingest:
            loaded_docs = []
            for filename in new_files_to_ingest:
                file_path = os.path.join(DATA_PATH, filename)
                if file_path.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding="utf-8")
                loaded_docs.extend(loader.load())
            
            if loaded_docs:
                chunks = split_documents(loaded_docs)
                add_to_chroma(chunks)

        chunk_count, updated_docs = get_db_stats_helper()
        return {
            "status": "success",
            "message": f"Successfully ingested {len(new_files_to_ingest)} new file(s).",
            "chunk_count": chunk_count,
            "documents": updated_docs
        }
    except Exception as e:
        print(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    """Execute similarity search against Chroma and synthesize answers via OpenAI GPT-4o-mini."""
    query_text = payload.query

    # 1. Verification checks
    openai_key = os.getenv("OPENAI_API_KEY")
    has_api_key = bool(openai_key and openai_key != "your_openai_api_key_here")
    if not has_api_key:
        return QueryResponse(
            answer="❌ **API Key Error:** OPENAI_API_KEY environment variable is not set or is still a placeholder. Please add your key to the `.env` file to enable the AI engine.",
            sources=[]
        )

    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        return QueryResponse(
            answer="⚠️ **Database Empty:** No documents have been indexed yet. Please upload files in the sidebar to populate the knowledge base.",
            sources=[]
        )

    try:
        # 2. Search Chroma vector store
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        results = db.similarity_search_with_score(query_text, k=5)
        
        if len(results) == 0:
            return QueryResponse(
                answer="🔍 **No Results:** I couldn't find any relevant document snippets matching your query.",
                sources=[]
            )

        # 3. Build synthesis context
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        # 4. Formulate LLM query
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt_template = ChatPromptTemplate.from_template(
            "Answer the question based ONLY on the following context. If you cannot find the answer in the context, "
            "say \"I could not find the answer in the provided documents.\" DO NOT make up information.\n\n"
            "Context:\n{context}\n\n---\n\nQuestion: {question}"
        )
        prompt = prompt_template.format(context=context_text, question=query_text)

        # 5. Call OpenAI API
        model = ChatOpenAI(
            model="gpt-4o-mini", 
            openai_api_key=openai_key,
            temperature=0.2
        )
        response_metadata = model.invoke(prompt)
        response_text = response_metadata.content

        # 6. Extract structured citations
        sources = []
        for doc, _score in results:
            doc_id = doc.metadata.get("id")
            if doc_id:
                source_file = os.path.basename(doc.metadata.get("source", "unknown"))
                page = doc.metadata.get("page", 0) + 1  # 1-indexed for humans
                
                # Fetch a short snippet of the actual matching text to show in the citation hover/modal!
                snippet = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                
                sources.append({
                    "file": source_file,
                    "page": page,
                    "snippet": snippet
                })
        
        # De-duplicate sources based on (file, page)
        seen_sources = set()
        unique_sources = []
        for s in sources:
            key = (s["file"], s["page"])
            if key not in seen_sources:
                seen_sources.add(key)
                unique_sources.append(s)

        return QueryResponse(answer=response_text, sources=unique_sources)

    except Exception as e:
        print(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a single document and all its corresponding vector chunks from the DB."""
    try:
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        
        # Get all records
        db_data = db.get(include=["metadatas"])
        ids_to_delete = []
        
        if db_data["metadatas"]:
            for idx, meta in enumerate(db_data["metadatas"]):
                if meta and "source" in meta:
                    source_file = os.path.basename(meta["source"])
                    if source_file == filename:
                        ids_to_delete.append(db_data["ids"][idx])
        
        # Perform deletion in vector store
        if ids_to_delete:
            db.delete(ids=ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} chunks from Chroma for {filename}")
            
        # Delete file from local storage
        file_path = os.path.join(DATA_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted physical file {file_path}")
            
        chunk_count, updated_docs = get_db_stats_helper()
        return {
            "status": "success",
            "message": f"Successfully deleted '{filename}' from system databases.",
            "chunk_count": chunk_count,
            "documents": updated_docs
        }
    except Exception as e:
        print(f"Deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_database():
    """Completely wipe the Chroma database and all source files."""
    try:
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH)
            
        # Recreate empty folders
        os.makedirs(DATA_PATH, exist_ok=True)
        os.makedirs(CHROMA_PATH, exist_ok=True)
        
        return {
            "status": "success",
            "message": "Vector DB and source repository wiped successfully.",
            "chunk_count": 0,
            "documents": []
        }
    except Exception as e:
        print(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load-sample")
async def load_sample():
    """Load the default Zero-G guidelines into the vector store as sample content."""
    sample_filename = "project_zerog_rules.md"
    sample_source_path = os.path.join(DATA_PATH, sample_filename)

    if not os.path.exists(sample_source_path):
        raise HTTPException(status_code=404, detail="Sample guide file not found on disk.")

    try:
        _, doc_list = get_db_stats_helper()
        if sample_filename not in doc_list:
            loader = TextLoader(sample_source_path, encoding="utf-8")
            loaded_docs = loader.load()
            chunks = split_documents(loaded_docs)
            add_to_chroma(chunks)
            
        chunk_count, updated_docs = get_db_stats_helper()
        return {
            "status": "success",
            "message": "Loaded zero-gravity guidelines sample file.",
            "chunk_count": chunk_count,
            "documents": updated_docs
        }
    except Exception as e:
        print(f"Sample loading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
