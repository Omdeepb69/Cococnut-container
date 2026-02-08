from fastapi import FastAPI, Depends, HTTPException, Body
from redis import Redis
import os
import security
import time
from brain import ModelEngine
from memory import ConversationMemory
from cache import SemanticCache

app = FastAPI(title="Coconut API", version="1.0.0")

# Redis Connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

# Initialize Core Components
brain = ModelEngine()
memory = ConversationMemory(redis_client)
cache = SemanticCache(redis_client)

@app.on_event("startup")
async def startup_event():
    # Load model on startup (this might take a while)
    brain.load_model()

@app.get("/")
def read_root(key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))):
    return {
        "message": "Welcome to Project Coconut API 🥥",
        "tier": key_data.get("tier", "unknown")
    }

@app.post("/chat")
def chat_endpoint(
    payload: dict = Body(...),
    key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))
):
    """
    Main chat endpoint with Memory, Cache, and RAG.
    """
    prompt = payload.get("prompt")
    session_id = payload.get("session_id", "default")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # 1. Search Knowledge Base (RAG)
    # Note: We are using 'cache' here as the interface to the Vector DB
    context = cache.search(prompt)
    
    final_prompt = prompt
    if context:
        print(f"RAG Context found: {context[:50]}...")
        final_prompt = f"Context: {context}\n\nQuestion: {prompt}"

    # 2. Retrieve Conversation History
    history = memory.get_history(session_id)

    # 3. Generate Response (Inference)
    response = brain.predict(final_prompt, history)

    # 4. Update Memory
    # We store the original user prompt, not the context-injected one, to keep history clean
    memory.add_message(session_id, "user", prompt)
    memory.add_message(session_id, "assistant", response)

    return {
        "response": response, 
        "source": "model", 
        "rag_context": context[:100] + "..." if context else None
    }

@app.get("/metrics")
def metrics():
    """
    Exports basic saturation and traffic metrics.
    For production, consider using prometheus-client to export real counters.
    """
    return {
        "inference_count": brain.inference_count if hasattr(brain, "inference_count") else 0,
        "cache_hits": cache.hits if hasattr(cache, "hits") else 0,
        "status": "healthy"
    }

@app.post("/generate-key")
def generate_key(tier: str = "free"):

    """
    Generates a new API key.
    IMPORTANT: The key is shown valid ONLY once. Store it safely.
    """
    if not redis_client:
        raise HTTPException(status_code=503, detail="Database unavailable")
        
    raw_key = security.generate_api_key()
    hashed_key = security.hash_api_key(raw_key)
    
    # Store hash in Redis
    redis_client.hset(f"apikey:{hashed_key}", mapping={
        "tier": tier,
        "created_at": time.time()
    })
    
    return {"api_key": raw_key, "tier": tier, "note": "Save this key! It won't be shown again."}

@app.get("/health")
def health_check():
    redis_status = "down"
    try:
        if redis_client and redis_client.ping():
            redis_status = "up"
    except Exception:
        pass
    
    return {
        "status": "ok",
        "redis": redis_status
    }
