"""MarketPilot AI - Configuration Management"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    # App
    APP_NAME: str = "MarketPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # RAG
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    
    # n8n
    N8N_WEBHOOK_URL: Optional[str] = os.getenv("N8N_WEBHOOK_URL")
    N8N_ENABLED: bool = os.getenv("N8N_ENABLED", "false").lower() == "true"
    
    # Data
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    DATA_DIR: str = "./data"
    KNOWLEDGE_BASE_DIR: str = "./knowledge_base"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on selected provider."""
        if self.LLM_PROVIDER == "gemini":
            return {"provider": "gemini", "api_key": self.GOOGLE_API_KEY, "model": self.GEMINI_MODEL}
        elif self.LLM_PROVIDER == "openai":
            return {"provider": "openai", "api_key": self.OPENAI_API_KEY, "model": self.OPENAI_MODEL}
        elif self.LLM_PROVIDER == "anthropic":
            return {"provider": "anthropic", "api_key": self.ANTHROPIC_API_KEY, "model": self.ANTHROPIC_MODEL}
        raise ValueError(f"Unknown LLM provider: {self.LLM_PROVIDER}")

settings = Settings()
