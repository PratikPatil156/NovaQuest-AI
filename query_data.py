import argparse
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from get_embedding_function import get_embedding_function

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based ONLY on the following context. If you cannot find the answer in the context, say "I could not find the answer in the provided documents." DO NOT make up information.

Context:
{context}

---

Question: {question}
"""

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query prompt to ask the RAG model.")
    args = parser.parse_args()
    
    query_text = args.query_text
    response = query_rag(query_text)
    print("\n💡 Response:")
    print(response)


def query_rag(query_text: str):
    # Verify API key is present
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        return "❌ Error: OPENAI_API_KEY environment variable is not set. Please add it to your .env file."

    # Verify vector DB exists
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        return "⚠️ Error: Database is empty. Please run 'populate_database.py' first to ingest documents."

    # Load persistent vector database
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB (retrieve top 5 matching chunks)
    results = db.similarity_search_with_score(query_text, k=5)
    
    if len(results) == 0:
        return "🔍 No matching documents found in the database."

    # Build context from retrieved chunks
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Format the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Load OpenAI LLM (gpt-4o-mini is smart, fast, and highly cost-effective)
    model = ChatOpenAI(
        model="gpt-4o-mini", 
        openai_api_key=openai_key,
        temperature=0.2
    )

    # Get response from the model
    response_metadata = model.invoke(prompt)
    response_text = response_metadata.content

    # Collect source details for citations
    sources = []
    for doc, _score in results:
        doc_id = doc.metadata.get("id")
        if doc_id:
            # Format nicely: filename (e.g., data/rules.pdf -> rules.pdf)
            source_file = os.path.basename(doc.metadata.get("source", "unknown"))
            page = doc.metadata.get("page", 0) + 1  # 0-indexed page in PyPDF, make it 1-indexed for humans
            sources.append(f"{source_file} (Page {page})")
    
    # De-duplicate sources list
    unique_sources = list(set(sources))
    
    # Format and append sources to response
    formatted_sources = "\n📚 Sources:\n" + "\n".join([f"- {s}" for s in unique_sources])
    
    return f"{response_text}\n\n{formatted_sources}"


if __name__ == "__main__":
    main()
