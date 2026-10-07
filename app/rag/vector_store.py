"""MarketPilot AI - Dual-Engine Vector Store
Supports ChromaDB with SentenceTransformers, and automatic fallback
to TF-IDF semantic vector similarity with Cosine Scoring.
"""
import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

logger = logging.getLogger("marketpilot.rag.vector_store")

@dataclass
class SearchResult:
    id: str
    content: str
    metadata: dict
    score: float

class RAGVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "marketpilot_knowledge"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.mode = "chroma"  # 'chroma' or 'tfidf'
        self.client = None
        self.collection = None
        
        # TF-IDF fallback store structures
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.doc_ids: List[str] = []
        self.vectorizer = None
        self.tfidf_matrix = None

    def initialize(self):
        """Initialize ChromaDB or fall back to high-performance TF-IDF vector store."""
        os.makedirs(self.persist_directory, exist_ok=True)
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
            self.mode = "chroma"
            logger.info("RAG Vector Store initialized using ChromaDB.")
        except Exception as e:
            logger.info(f"ChromaDB not available ({e}). Using native TF-IDF vector engine.")
            self.mode = "tfidf"
            self._load_tfidf_state()

    def _get_tfidf_filepath(self) -> str:
        return os.path.join(self.persist_directory, f"{self.collection_name}_store.json")

    def _load_tfidf_state(self):
        filepath = self._get_tfidf_filepath()
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.doc_ids = data.get("doc_ids", [])
                if self.documents:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
                    self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            except Exception as e:
                logger.warning(f"Could not load persistent TF-IDF state: {e}")

    def _save_tfidf_state(self):
        filepath = self._get_tfidf_filepath()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "documents": self.documents,
                    "metadatas": self.metadatas,
                    "doc_ids": self.doc_ids
                }, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save TF-IDF state: {e}")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        if not documents:
            return

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        if self.mode == "chroma" and self.collection is not None:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                return
            except Exception as e:
                logger.warning(f"Chroma add_documents error ({e}). Switching to TF-IDF vector engine.")
                self.mode = "tfidf"

        # TF-IDF addition
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.doc_ids.extend(ids)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        self._save_tfidf_state()

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not query:
            return []

        if self.mode == "chroma" and self.collection is not None:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
                search_results = []
                if results and results.get('ids') and len(results['ids']) > 0:
                    for i in range(len(results['ids'][0])):
                        search_results.append(SearchResult(
                            id=results['ids'][0][i],
                            content=results['documents'][0][i],
                            metadata=results['metadatas'][0][i] if results.get('metadatas') else {},
                            score=float(results['distances'][0][i]) if 'distances' in results and results['distances'] else 0.0
                        ))
                return search_results
            except Exception as e:
                logger.warning(f"Chroma query failed ({e}). Falling back to TF-IDF.")

        # TF-IDF vector similarity search
        if not self.documents or self.vectorizer is None or self.tfidf_matrix is None:
            self._load_tfidf_state()

        if not self.documents or self.vectorizer is None:
            return []

        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]

        search_results = []
        for idx in top_indices:
            score = float(similarities[idx])
            search_results.append(SearchResult(
                id=self.doc_ids[idx],
                content=self.documents[idx],
                metadata=self.metadatas[idx] if idx < len(self.metadatas) else {},
                score=round(score, 4)
            ))
        return search_results

    def delete_collection(self):
        if self.mode == "chroma" and self.client:
            try:
                self.client.delete_collection(name=self.collection_name)
                self.collection = None
            except Exception:
                pass
        self.documents = []
        self.metadatas = []
        self.doc_ids = []
        self.vectorizer = None
        self.tfidf_matrix = None
        filepath = self._get_tfidf_filepath()
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

    def get_collection_stats(self) -> dict:
        if self.mode == "chroma" and self.collection:
            try:
                return {"count": self.collection.count(), "mode": "chromadb"}
            except Exception:
                pass
        return {"count": len(self.documents), "mode": "tfidf_vector_engine"}
