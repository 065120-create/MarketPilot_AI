import os
import glob
from app.rag.vector_store import RAGVectorStore
from app.rag.metadata import build_metadata

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
        
    return chunks

def process_markdown(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return chunk_text(content)

def extract_metadata(filepath: str, chunk: str, chunk_index: int) -> dict:
    return build_metadata(filepath, chunk_index, chunk)

def ingest_knowledge_base(knowledge_dir: str) -> dict:
    store = RAGVectorStore()
    store.initialize()
    
    md_files = glob.glob(os.path.join(knowledge_dir, "**/*.md"), recursive=True)
    
    total_docs = 0
    total_chunks = 0
    
    for filepath in md_files:
        chunks = process_markdown(filepath)
        if not chunks:
            continue
            
        metadatas = [extract_metadata(filepath, chunk, i) for i, chunk in enumerate(chunks)]
        store.add_documents(documents=chunks, metadatas=metadatas)
        
        total_docs += 1
        total_chunks += len(chunks)
        
    return {
        "files_processed": total_docs,
        "chunks_added": total_chunks,
        "store_stats": store.get_collection_stats()
    }
