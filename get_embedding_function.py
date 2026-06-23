import os
from langchain_openai import OpenAIEmbeddings

def get_embedding_function():
    """Retrieve the embedding function using OpenAI text-embedding-3-small."""
    try:
        # Load the OpenAI API Key from .env manually as per original script custom parsing
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    os.environ["OPENAI_API_KEY"] = key
    except FileNotFoundError:
        raise FileNotFoundError("Error: .env file not found in directory.")

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY is empty, unset, or still a placeholder in your .env file.")

    # Initialize OpenAI Embeddings (text-embedding-3-small is high speed & precision)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )
    return embeddings