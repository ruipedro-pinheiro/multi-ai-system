"""Configuration for Multi-AI System - Privacy-first, multi-provider setup"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union

class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./multi-ai-system.db"
    
    # CORS
    cors_origins: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # LiteLLM Configuration (supports 100+ providers)
    # Priority: 1 = Try first (cheapest/local), 2 = Fallback (cloud)
    
    # Ollama (Local, Free, Privacy-first) - PRIORITY 1
    ollama_base_url: Optional[str] = None
    ollama_model: str = "llama2"  # or llama3, mistral, etc.
    
    # Claude (Fallback) - PRIORITY 2
    anthropic_api_key: Optional[str] = None
    
    # OpenAI (Fallback) - PRIORITY 3
    openai_api_key: Optional[str] = None
    
    # Google Gemini (FREEMIUM - gratuit) - PRIORITY 1
    google_api_key: Optional[str] = None
    
    # Groq (FREEMIUM - gratuit, ultra rapide) - PRIORITY 1
    groq_api_key: Optional[str] = None
    
    # Mem0 Memory Layer (Token Optimization)
    mem0_api_key: Optional[str] = None
    mem0_enabled: bool = True
    
    # Qdrant Vector DB (for memory storage)
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "multi-ai-system_memory"
    
    class Config:
        env_file = ".env"

settings = Settings()
