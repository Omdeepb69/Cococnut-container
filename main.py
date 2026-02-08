from fastapi import FastAPI, Depends, HTTPException, Body
from redis import Redis
from config import config
import security
import time
from brain import ModelEngine
from memory import ConversationMemory
from cache import SemanticMapper

app = FastAPI(title="S-Tier Coconut API", version="1.1.0")

# Redis Connection using Config
try:
    redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

# Initialize Core Components
brain = ModelEngine()
memory = ConversationMemory(redis_client)
mapper = SemanticMapper(redis_client)

@app.on_event("startup")
async def startup_event():
    brain.load_model()

@app.get("/")
def read_root(key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))):
    return {
        "message": "Welcome to S-Tier Project Coconut 🥥",
        "model": config.MODEL_ID,
        "device": brain.device
    }

@app.post("/chat")
def chat_endpoint(
    payload: dict = Body(...),
    key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))
):
    prompt = payload.get("prompt")
    session_id = payload.get("session_id", "default")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # 1. SEMANTIC CACHE (Check if we already answered this)
    if config.ENABLE_CACHE:
        cached_res = mapper.get_cached_response(prompt)
        if cached_res:
            return {
                "response": cached_res,
                "source": "semantic_cache",
                "rag_context": None
            }

    # 2. RAG (Augment prompt if no cache hit)
    context = None
    if config.ENABLE_RAG:
        context = mapper.get_context(prompt)
    
    final_prompt = prompt
    if context:
        final_prompt = f"Context: {context}\n\nQuestion: {prompt}"

    # 3. MEMORY (Retrieve History)
    history = []
    if config.ENABLE_MEMORY:
        history = memory.get_history(session_id)

    # 4. INFERENCE (Generate Response)
    response = brain.predict(final_prompt, history)

    # 5. POST-PROCESS (Store results)
    if config.ENABLE_MEMORY:
        memory.add_message(session_id, "user", prompt)
        memory.add_message(session_id, "assistant", response)
    
    if config.ENABLE_CACHE:
        mapper.store_cache(prompt, response)

    return {
        "response": response, 
        "source": "model", 
        "rag_context": context[:100] + "..." if context else None
    }

@app.get("/metrics")
def metrics():
    return {
        "inference_count": brain.inference_count,
        "cache_hits": mapper.hits,
        "device": brain.device,
        "model": config.MODEL_ID,
        "features": {
            "rag": config.ENABLE_RAG,
            "cache": config.ENABLE_CACHE,
            "memory": config.ENABLE_MEMORY
        }
    }

@app.post("/generate-key")
def generate_key(tier: str = "free"):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Database unavailable")
        
    raw_key = security.generate_api_key()
    hashed_key = security.hash_api_key(raw_key)
    
    redis_client.hset(f"apikey:{hashed_key}", mapping={
        "tier": tier,
        "created_at": time.time()
    })
    
    return {
        "api_key": raw_key, 
        "tier": tier, 
        "limit": config.RATE_LIMIT_PRO if tier == "pro" else config.RATE_LIMIT_FREE,
        "window": config.RATE_WINDOW
    }

@app.get("/health")
def health_check():
    redis_status = "up" if (redis_client and redis_client.ping()) else "down"
    return {"status": "ok", "redis": redis_status}
