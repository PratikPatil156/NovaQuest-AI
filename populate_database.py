import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    # Check if database should be cleared (using --reset flag)
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created '{DATA_PATH}' directory. Place your documents here.")

    # Create chroma directory if it doesn't exist
    if not os.path.exists(CHROMA_PATH):
        os.makedirs(CHROMA_PATH)

    # 1. Load documents
    documents = load_documents()
    if not documents:
        print("No documents found. Add some PDFs or TXT files to the 'data/' directory.")
        return

    # 2. Split documents into chunks
    chunks = split_documents(documents)

    # 3. Add to vector store
    add_to_chroma(chunks)


def load_documents():
    documents = []
    
    # Load PDFs if any exist
    if os.path.exists(DATA_PATH):
        pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
        pdf_docs = pdf_loader.load()
        documents.extend(pdf_docs)
        if pdf_docs:
            print(f"Loaded {len(pdf_docs)} pages from PDF documents.")

        # Load Text / Markdown files if any exist
        txt_loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
        txt_docs = txt_loader.load()
        documents.extend(txt_docs)
        if txt_docs:
            print(f"Loaded {len(txt_docs)} text documents.")

        md_loader = DirectoryLoader(DATA_PATH, glob="*.md", loader_cls=TextLoader)
        md_docs = md_loader.load()
        documents.extend(md_docs)
        if md_docs:
            print(f"Loaded {len(md_docs)} markdown documents.")

    return documents


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=40,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


def add_to_chroma(chunks: list[Document]):
    # Load the existing database
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=get_embedding_function()
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents
    existing_items = db.get(include=[])  # ids are always returned by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that do not exist in the DB
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding {len(new_chunks)} new chunks to the database...")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        
        # Batch insert to avoid size limits in SQLite/Chroma
        batch_size = 100
        for i in range(0, len(new_chunks), batch_size):
            batch_chunks = new_chunks[i : i + batch_size]
            batch_ids = new_chunk_ids[i : i + batch_size]
            db.add_documents(batch_chunks, ids=batch_ids)
        
        print("Database updated successfully!")
    else:
        print("No new documents to add. Database is up to date!")


def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", 0)
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page metadata
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("Database wiped clean.")


if __name__ == "__main__":
    main()
