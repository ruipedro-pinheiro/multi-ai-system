"""Configuration for Multi-AI System - Privacy-first, multi-provider setup"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union

class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    project_name: str = "chika"
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    api_port: int = 8000
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    session_limit_per_minute: int = 5
    
    # Database
    database_url: str = "sqlite:///./chika.db"
    
    # CORS
    cors_origins: Union[List[str], str] = [
        "http://localhost:3001",
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://ruipedro-pinheiro.github.io"
    ]
    
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
    qdrant_collection: str = "chika_memory"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from .env
        case_sensitive = False

import os
from pathlib import Path

# Force load .env from backend directory
env_path = Path(__file__).parent / ".env"
settings = Settings(_env_file=str(env_path))
