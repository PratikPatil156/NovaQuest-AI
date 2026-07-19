import os
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function():
    # Use HuggingFace local multilingual embeddings to support Hinglish/Hindi
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    return embeddings