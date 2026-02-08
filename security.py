import secrets
import hashlib
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from redis import Redis
import time

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def generate_api_key(prefix: str = "cc_live_") -> str:
    """Generates a secure random API key."""
    return f"{prefix}{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hashes the API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(
    api_key: str = Security(API_KEY_HEADER), 
    redis_client: Redis = None
):
    """
    Verifies the API key and enforces rate limits.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )

    if not redis_client:
        # Fallback if Redis is down, though in prod we might want to fail closed
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security service unavailable"
        )
        
    hashed_key = hash_api_key(api_key)
    key_data = redis_client.hgetall(f"apikey:{hashed_key}")

    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    # Rate Limiting Logic (Atomic Window)
    tier = key_data.get("tier", "free")
    limit = 10 if tier == "free" else 100 
    
    limit_key = f"usage:{hashed_key}"
    
    # Atomic Increment
    request_count = redis_client.incr(limit_key)

    # If this is the first request in the window, set the 60s timer
    if request_count == 1:
        redis_client.expire(limit_key, 60)

    if request_count > limit:
        ttl = redis_client.ttl(limit_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )

    return key_data
