import os
from typing import Optional

class Config:
    # Model Configuration
    MODEL_ID: str = os.getenv("MODEL_ID", "omdeep22/Gonyai-v1")
    EMBEDDING_MODEL_ID: str = os.getenv("EMBEDDING_MODEL_ID", "all-MiniLM-L6-v2")
    
    # Feature Flags
    ENABLE_RAG: bool = os.getenv("ENABLE_RAG", "True").lower() == "true"
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    ENABLE_MEMORY: bool = os.getenv("ENABLE_MEMORY", "True").lower() == "true"
    
    # Infrastructure
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6380))
    
    # Hardware/Performance
    DEVICE: str = os.getenv("DEVICE", "auto") # auto, cuda, cpu
    CACHE_THRESHOLD: float = float(os.getenv("CACHE_THRESHOLD", 0.85))
    
    # Security tiers
    RATE_LIMIT_FREE: int = 10
    RATE_LIMIT_PRO: int = 100
    RATE_WINDOW: int = 60 # seconds

config = Config()
