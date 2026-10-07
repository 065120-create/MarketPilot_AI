import sys
import os

# Assuming app.rag.retriever will be available
try:
    from app.rag.retriever import RAGRetriever
except ImportError:
    RAGRetriever = None

class RAGTool:
    def __init__(self):
        self.retriever = RAGRetriever() if RAGRetriever else None

    def search_knowledge(self, query: str, top_k: int = 5) -> list:
        if not self.retriever:
            return [{"error": "RAG Retriever not initialized"}]
        
        results = self.retriever.search(query, top_k=top_k)
        return [{"content": r.content, "metadata": r.metadata, "score": r.score} for r in results]

    def search_with_context(self, query: str, context: str, top_k: int = 5) -> list:
        enhanced_query = f"{context} {query}"
        return self.search_knowledge(enhanced_query, top_k)

    def get_relevant_frameworks(self, topic: str) -> list:
        query = f"marketing framework strategy for {topic}"
        return self.search_knowledge(query, top_k=3)

# Expose functional interface
_tool = RAGTool()

def search_knowledge(query: str, top_k: int = 5) -> list:
    return _tool.search_knowledge(query, top_k)

def search_with_context(query: str, context: str, top_k: int = 5) -> list:
    return _tool.search_with_context(query, context, top_k)

def get_relevant_frameworks(topic: str) -> list:
    return _tool.get_relevant_frameworks(topic)
