import secrets
import hashlib
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from redis import Redis
import time

from config import config

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
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )

    if not redis_client:
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

    # Use S-Tier Configuration for limits
    tier = key_data.get("tier", "free")
    limit = config.RATE_LIMIT_PRO if tier == "pro" else config.RATE_LIMIT_FREE
    window = config.RATE_WINDOW
    
    limit_key = f"usage:{hashed_key}"
    request_count = redis_client.incr(limit_key)

    if request_count == 1:
        redis_client.expire(limit_key, window)

    if request_count > limit:
        ttl = redis_client.ttl(limit_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )

    return key_data

    return key_data
