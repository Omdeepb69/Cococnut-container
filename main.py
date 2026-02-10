from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse, Response
from redis import Redis
from config import config
import security
import time
import json
from brain import ModelEngine
from memory import ConversationMemory
from cache import SemanticMapper
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Gonyai Production API", version="1.2.0")

# Prometheus Metrics
CACHE_STATS = Counter('gonyai_cache_requests_total', 'Total cache requests', ['status'])
INFERENCE_LATENCY = Histogram('gonyai_inference_latency_seconds', 'Time spent processing AI inference')
API_REQUESTS = Counter('gonyai_api_requests_total', 'Total API requests', ['endpoint', 'tier'])

# Redis Connection using Config
try:
    redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

# Initialize Core Components
brain = ModelEngine()
memory = ConversationMemory(redis_client)
# Cache versioned by model to prevent logical drift
mapper = SemanticMapper(redis_client, model_hash=brain.get_model_hash())

@app.on_event("startup")
async def startup_event():
    brain.load_model()

@app.get("/")
def read_root(key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))):
    API_REQUESTS.labels(endpoint="/", tier=key_data['tier']).inc()
    return {
        "message": "Welcome to Gonyai Production AI Engine 🥥🤖",
        "model": config.MODEL_ID,
        "device": brain.device,
        "quantization": "4-bit" if config.LOAD_IN_4BIT else ("8-bit" if config.LOAD_IN_8BIT else "None")
    }

@app.post("/chat")
def chat_endpoint(
    payload: dict = Body(...),
    key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))
):
    API_REQUESTS.labels(endpoint="/chat", tier=key_data['tier']).inc()
    prompt = payload.get("prompt")
    session_id = payload.get("session_id", "default")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # 1. SEMANTIC CACHE
    if config.ENABLE_CACHE:
        cached_res = mapper.get_cached_response(prompt)
        if cached_res:
            CACHE_STATS.labels(status='hit').inc()
            return {
                "response": cached_res,
                "source": "semantic_cache",
                "rag_context": None
            }
        CACHE_STATS.labels(status='miss').inc()

    # 2. RAG
    context = mapper.get_context(prompt) if config.ENABLE_RAG else None
    final_prompt = f"Context: {context}\n\nQuestion: {prompt}" if context else prompt

    # 3. MEMORY
    history = memory.get_history(session_id) if config.ENABLE_MEMORY else []

    # 4. INFERENCE
    start_time = time.time()
    with INFERENCE_LATENCY.time():
        response = brain.predict(final_prompt, history)
    
    # 5. POST-PROCESS
    if config.ENABLE_MEMORY:
        memory.add_message(session_id, "user", prompt)
        memory.add_message(session_id, "assistant", response)
    
    if config.ENABLE_CACHE:
        mapper.store_cache(prompt, response)

    return {
        "response": response, 
        "source": "model", 
        "inference_time": round(time.time() - start_time, 2),
        "rag_context": context[:100] + "..." if context else None
    }

@app.post("/chat/stream")
async def chat_stream_endpoint(
    payload: dict = Body(...),
    key_data: dict = Depends(lambda k=Depends(security.API_KEY_HEADER): security.verify_api_key(k, redis_client))
):
    """Real-time streaming endpoint for high-end UX."""
    API_REQUESTS.labels(endpoint="/chat/stream", tier=key_data['tier']).inc()
    prompt = payload.get("prompt")
    session_id = payload.get("session_id", "default")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # 1. Check Cache first
    if config.ENABLE_CACHE:
        cached_res = mapper.get_cached_response(prompt)
        if cached_res:
            CACHE_STATS.labels(status='hit').inc()
            async def stream_cached():
                yield f"data: {json.dumps({'token': cached_res, 'source': 'semantic_cache'})}\n\n"
            return StreamingResponse(stream_cached(), media_type="text/event-stream")

    CACHE_STATS.labels(status='miss').inc()
    context = mapper.get_context(prompt) if config.ENABLE_RAG else None
    final_prompt = f"Context: {context}\n\nQuestion: {prompt}" if context else prompt
    history = memory.get_history(session_id) if config.ENABLE_MEMORY else []

    async def event_generator():
        full_response = ""
        for token in brain.stream_predict(final_prompt, history):
            full_response += token
            yield f"data: {json.dumps({'token': token, 'source': 'model'})}\n\n"
        
        if config.ENABLE_MEMORY:
            memory.add_message(session_id, "user", prompt)
            memory.add_message(session_id, "assistant", full_response)
        if config.ENABLE_CACHE:
            mapper.store_cache(prompt, full_response)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/metrics")
def metrics():
    """Standard Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate-key")
def generate_key(
    tier: str = "free",
    admin_key: str = Depends(lambda k=Depends(security.API_KEY_HEADER): k)
):
    """Protected admin endpoint to prevent key spamming."""
    if admin_key != config.ADMIN_ROOT_KEY:
        raise HTTPException(status_code=403, detail="Admin credentials required")
        
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

@app.get("/health/ready")
def readiness_check():
    """Specific probe for K8s to detect when the AI Brain is loaded."""
    if not brain.ready:
        raise HTTPException(status_code=503, detail="Model still loading")
    return {"status": "ready"}
