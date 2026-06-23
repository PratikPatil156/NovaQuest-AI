import streamlit as st
import os
import shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from get_embedding_function import get_embedding_function
from populate_database import split_documents, add_to_chroma
from query_data import query_rag

# Load environment variables
load_dotenv()

# Define paths
CHROMA_PATH = "chroma"
DATA_PATH = "data"

# Ensure folders exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

# ----------------- UI CONFIG & THEMING -----------------
st.set_page_config(
    page_title="GraviRAG - Zero-G Knowledge Engine",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Sleek CSS
st.markdown("""
<style>
    /* Main Background & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Elegant Title and Header styling */
    .title-gradient {
        background: linear-gradient(135deg, #00FFA3, #03E2FF, #8E2DE2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0px;
        padding-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: #A3ABB7;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Styling Side bar and Metrics */
    .metric-card {
        background-color: #1E2330;
        border-radius: 12px;
        padding: 15px 20px;
        border: 1px solid #2D3548;
        margin-bottom: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 163, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #8A94A6;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 5px;
    }
    
    /* Upload Section */
    .uploader-card {
        background-color: #131722;
        border-radius: 12px;
        border: 2px dashed #00FFA3;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #5A627A;
        font-size: 0.85rem;
        margin-top: 5rem;
        border-top: 1px solid #1E2330;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- DB INFORMATION RETRIEVAL -----------------
def get_db_stats():
    """Retrieve metadata information from the Chroma database."""
    try:
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
    except Exception:
        return 0, []

# ----------------- SIDEBAR INTERFACE -----------------
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/gravity.png", width=64)
    st.markdown("<h2 style='color:#FFFFFF; margin-top:0px;'>GraviRAG Control</h2>", unsafe_allow_html=True)
    st.markdown("Your interactive RAG-powered workspace documentation assistant.")
    
    st.markdown("---")
    
    # Live stats
    chunk_count, doc_list = get_db_stats()
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Active Chunks</div>
        <div class="metric-val">{chunk_count}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Ingested Docs</div>
        <div class="metric-val">{len(doc_list)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Document uploader inside the sidebar
    st.markdown("### 📥 Ingest Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs or Text files to instantly populate your vector space:",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        with st.spinner("Processing documents..."):
            new_files_to_ingest = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_PATH, uploaded_file.name)
                
                # Check if it's already in the vector database to avoid redundant work
                if uploaded_file.name not in doc_list:
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    new_files_to_ingest.append(uploaded_file.name)
            
            if new_files_to_ingest:
                try:
                    from langchain_community.document_loaders import PyPDFLoader, TextLoader
                    
                    loaded_docs = []
                    for filename in new_files_to_ingest:
                        file_path = os.path.join(DATA_PATH, filename)
                        if file_path.endswith(".pdf"):
                            loader = PyPDFLoader(file_path)
                        else:
                            loader = TextLoader(file_path)
                        loaded_docs.extend(loader.load())
                    
                    # Split and save to Chroma DB
                    chunks = split_documents(loaded_docs)
                    add_to_chroma(chunks)
                    st.success("✅ New files ingested!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing files: {e}")
    
    # Show active files list
    if doc_list:
        st.markdown("### 📄 Managed Documents:")
        for doc in doc_list:
            st.markdown(f"- `{doc}`")
    else:
        st.info("No documents uploaded yet.")
        
    st.markdown("---")
    
    # Wipe database button
    if st.button("🗑️ Reset Vector Space", use_container_width=True):
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH)
        os.makedirs(DATA_PATH, exist_ok=True)
        os.makedirs(CHROMA_PATH, exist_ok=True)
        st.success("Wiped vector space and local files!")
        st.rerun()

# ----------------- MAIN INTERFACE -----------------
st.markdown("<h1 class='title-gradient'>🛸 GraviRAG Engine</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Knowledge Retrieval & Synthesis for Zero-Gravity Workflows, powered by Gemini</div>", unsafe_allow_html=True)

# Verify Gemini API key is configured
if not os.getenv("GEMINI_API_KEY"):
    st.warning("⚠️ **API Key Missing:** Please add your `GEMINI_API_KEY` to the `.env` file to start using the system.")
    st.info("You can get a free key from the [Google AI Studio](https://aistudio.google.com/).")
else:
    # Quick start instructions if DB is empty
    if chunk_count == 0:
        st.info("👋 **Welcome to GraviRAG!** To get started, upload a PDF or text file in the sidebar, or ask a question once you do.")
        
        # Option to quickly load sample files if they exist in standard folders
        if os.path.exists(os.path.join(DATA_PATH, "project_zerog_rules.md")):
            if st.button("🚀 Load Sample Zero-G Office Guidelines", type="primary"):
                with st.spinner("Ingesting sample file..."):
                    try:
                        from langchain_community.document_loaders import TextLoader
                        loader = TextLoader(os.path.join(DATA_PATH, "project_zerog_rules.md"))
                        chunks = split_documents(loader.load())
                        add_to_chroma(chunks)
                        st.success("Sample guidelines loaded!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading sample file: {e}")

    # Chat interface initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Receive new query
    if prompt := st.chat_input("Ask GraviRAG about your documentation..."):
        # Append user query to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response using RAG engine
        with st.chat_message("assistant"):
            with st.spinner("Scanning vector databases and synthesizing answer..."):
                response = query_rag(prompt)
                st.markdown(response)
                
        # Append response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("<div class='footer'>GraviRAG Engine • Powered by LangChain, ChromaDB, and Google Gemini API</div>", unsafe_allow_html=True)
