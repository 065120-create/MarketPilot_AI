from typing import List, Optional
from dataclasses import dataclass
from app.rag.vector_store import RAGVectorStore, SearchResult

@dataclass
class RAGChunk:
    content: str
    metadata: dict
    score: float

class RAGRetriever:
    def __init__(self):
        self.store = RAGVectorStore()
        self.store.initialize()

    def search(self, query: str, top_k: int = 5, filter_metadata: dict = None) -> List[RAGChunk]:
        results = self.store.search(query, top_k=top_k)
        chunks = []
        for r in results:
            # Apply rudimentary metadata filtering if provided
            if filter_metadata:
                match = all(r.metadata.get(k) == v for k, v in filter_metadata.items())
                if not match:
                    continue
            chunks.append(RAGChunk(content=r.content, metadata=r.metadata, score=r.score))
        return chunks

    def search_with_reranking(self, query: str, top_k: int = 5) -> List[RAGChunk]:
        # Fetch more candidates and return top_k (dummy reranking logic for now)
        candidates = self.search(query, top_k=top_k * 2)
        # In a real system, a cross-encoder would score candidates here
        # Returning top_k sorted by existing score
        candidates.sort(key=lambda x: x.score)
        return candidates[:top_k]

    def should_retrieve(self, agent_name: str, task_description: str) -> bool:
        """
        Agentic RAG decision logic based on the task description.
        """
        task_lower = task_description.lower()
        trigger_keywords = [
            "framework", "best practice", "strategy", "benchmark",
            "historical", "guide", "concept", "theory", "explain"
        ]
        
        if any(kw in task_lower for kw in trigger_keywords):
            return True
            
        if agent_name.lower() in ["strategist", "planner"]:
            return True
            
        return False

    def format_context(self, chunks: List[RAGChunk]) -> str:
        if not chunks:
            return "No relevant context found."
            
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get('source', 'Unknown')
            context_parts.append(f"--- Document {i} (Source: {source}) ---\n{chunk.content}\n")
            
        return "\n".join(context_parts)
