import pytest
from langchain_core.documents import Document
from populate_database import calculate_chunk_ids

def test_calculate_chunk_ids():
    # GIVEN: A list of split document chunks
    chunk_1 = Document(page_content="Hello world chunk 1", metadata={"source": "data/test.pdf", "page": 0})
    chunk_2 = Document(page_content="Hello world chunk 2", metadata={"source": "data/test.pdf", "page": 0})
    chunk_3 = Document(page_content="Hello world chunk 3", metadata={"source": "data/test.pdf", "page": 1})
    
    chunks = [chunk_1, chunk_2, chunk_3]
    
    # WHEN: Calculating chunk IDs
    result = calculate_chunk_ids(chunks)
    
    # THEN: The IDs must be calculated correctly based on source:page:index format
    assert len(result) == 3
    assert result[0].metadata["id"] == "data/test.pdf:0:0"
    assert result[1].metadata["id"] == "data/test.pdf:0:1"
    assert result[2].metadata["id"] == "data/test.pdf:1:0"

def test_calculate_chunk_ids_missing_metadata():
    # GIVEN: Chunks with missing metadata keys (should fallback gracefully)
    chunk_1 = Document(page_content="No metadata chunk", metadata={})
    
    # WHEN: Calculating chunk IDs
    result = calculate_chunk_ids([chunk_1])
    
    # THEN: Fallback works and ID is generated
    assert len(result) == 1
    assert result[0].metadata["id"] == "None:0:0"
