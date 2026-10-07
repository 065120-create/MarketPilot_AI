"""Tests for Dual-Engine RAG Vector Store and Knowledge Retrieval."""
import pytest
from app.rag.ingest import chunk_text
from app.rag.vector_store import RAGVectorStore
from app.rag.retriever import RAGRetriever

def test_chunk_text():
    text = " ".join([f"word{i}" for i in range(1200)])
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 3
    # First chunk has 500 words
    assert len(chunks[0].split()) == 500

def test_rag_vector_store_add_and_search(tmp_path):
    store = RAGVectorStore(persist_directory=str(tmp_path), collection_name="test_kb")
    store.initialize()
    
    docs = [
        "Customer Lifetime Value (CLV) is calculated by multiplying average order value with purchase frequency.",
        "Return on Ad Spend (ROAS) equals total campaign revenue divided by total advertising spend.",
        "The AIDA marketing funnel tracks Attention, Interest, Desire, and Action across touchpoints."
    ]
    metadatas = [
        {"framework": "clv_formula", "source": "kpi.md"},
        {"framework": "roas_formula", "source": "budget.md"},
        {"framework": "aida_funnel", "source": "journey.md"}
    ]
    
    store.add_documents(docs, metadatas)
    
    # Query for ROAS
    results = store.search("how do I calculate ad spend return?", top_k=2)
    assert len(results) > 0
    # Top result should mention ROAS or revenue
    top_content = results[0].content.lower()
    assert "roas" in top_content or "revenue" in top_content or "ad spend" in top_content

def test_rag_retriever_agentic_decision():
    retriever = RAGRetriever()
    
    # Needs retrieval
    assert retriever.should_retrieve("optimization_agent", "Consult the marketing framework for budget rebalancing") is True
    assert retriever.should_retrieve("strategist", "Analyze campaign performance") is True
    
    # Does not need retrieval
    assert retriever.should_retrieve("simple_counter", "Count rows in dataframe") is False

def test_rag_format_context():
    retriever = RAGRetriever()
    from app.rag.retriever import RAGChunk
    chunks = [
        RAGChunk(content="Rule 1: Always cap channel budget at 50%", metadata={"source": "governance.md"}, score=0.92),
        RAGChunk(content="Rule 2: ROAS below 2.0 indicates fatigue", metadata={"source": "kpis.md"}, score=0.88)
    ]
    formatted = retriever.format_context(chunks)
    assert "Rule 1" in formatted
    assert "governance.md" in formatted
    assert "Rule 2" in formatted
