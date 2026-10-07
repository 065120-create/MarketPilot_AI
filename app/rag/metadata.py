import os
from collections import Counter
import re

class DocumentMetadata:
    def __init__(self, filepath: str, chunk_index: int, chunk_text: str):
        self.filepath = filepath
        self.chunk_index = chunk_index
        self.chunk_text = chunk_text

    def to_dict(self) -> dict:
        return {
            "source": os.path.basename(self.filepath),
            "path": self.filepath,
            "chunk_index": self.chunk_index,
            "topic": extract_topic(self.chunk_text),
            "keywords": ",".join(extract_keywords(self.chunk_text))
        }

def extract_topic(text: str) -> str:
    text_lower = text.lower()
    topics = {
        "strategy": ["strategy", "plan", "framework", "goal"],
        "analytics": ["data", "metrics", "analysis", "dashboard"],
        "budget": ["budget", "spend", "cost", "allocation", "roi"],
        "audience": ["segment", "customer", "demographic", "audience"],
        "content": ["content", "copy", "creative", "asset"]
    }
    
    scores = {topic: sum(1 for kw in kws if kw in text_lower) for topic, kws in topics.items()}
    best_topic = max(scores, key=scores.get)
    return best_topic if scores[best_topic] > 0 else "general"

def extract_keywords(text: str, n: int = 5) -> list:
    if not text:
        return []
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {'the', 'a', 'to', 'and', 'is', 'in', 'of', 'for', 'on', 'with', 'as', 'by', 'this', 'that'}
    valid_words = [w for w in words if w not in stop_words and len(w) > 3]
    counts = Counter(valid_words)
    return [word for word, _ in counts.most_common(n)]

def build_metadata(filepath: str, chunk_index: int, chunk_text: str) -> dict:
    meta = DocumentMetadata(filepath, chunk_index, chunk_text)
    return meta.to_dict()
