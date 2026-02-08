import sys
import numpy as np
from redis import Redis
from sentence_transformers import SentenceTransformer
from config import config

INDEX_NAME = "coconut_idx"

def ingest(text: str, source: str = "manual"):
    if not text.strip():
        return

    # 1. Connect
    r = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    
    # 2. Embed
    print(f"Embedding knowledge Using {config.EMBEDDING_MODEL_ID}...")
    model = SentenceTransformer(config.EMBEDDING_MODEL_ID)
    
    # 3. Create Index if needed
    try:
        r.execute_command("FT.INFO", INDEX_NAME)
    except:
        print("Creating Vector Index...")
        dim = 384 # Default for all-MiniLM-L6-v2
        r.execute_command(
            "FT.CREATE", INDEX_NAME, "ON", "HASH", "PREFIX", "1", "doc:",
            "SCHEMA", "content", "TEXT", "vector", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32", "DIM", str(dim), "DISTANCE_METRIC", "COSINE"
        )

    # 4. Store
    import hashlib
    doc_id = hashlib.md5(text.encode()).hexdigest()
    vector = model.encode(text).astype(np.float32).tobytes()
    
    r.hset(f"doc:{doc_id}", mapping={
        "content": text,
        "source": source,
        "vector": vector
    })
    print(f"Successfully ingested: {text[:50]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ingest.py \"Your knowledge text here\"")
        sys.exit(1)
    
    input_text = sys.argv[1]
    ingest(input_text)
