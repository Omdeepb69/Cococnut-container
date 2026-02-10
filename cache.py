import numpy as np
import hashlib
from redis import Redis
from typing import Optional
from config import config

INDEX_NAME = "coconut_idx"
CACHE_INDEX_NAME = "coconut_cache_idx"

class SemanticMapper:
    def __init__(self, redis_client: Redis, model_hash: str = "v1"):
        self.redis = redis_client
        self._model = None
        self.hits = 0
        self.cache_idx = f"cache_idx_{model_hash}"

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"Loading S-Tier Embedding Model: {config.EMBEDDING_MODEL_ID}...")
            self._model = SentenceTransformer(config.EMBEDDING_MODEL_ID)
        return self._model

    def get_context(self, prompt: str, top_k: int = 2) -> Optional[str]:
        """
        RAG: Retrieves relevant snippets to GROUND the model.
        """
        if not config.ENABLE_RAG or not self.redis:
            return None
        
        return self._search_vector_db(INDEX_NAME, prompt, top_k)

    def get_cached_response(self, prompt: str) -> Optional[str]:
        """
        Semantic Cache: Retrieves a PREVIOUS ANSWER to bypass inference.
        """
        if not config.ENABLE_CACHE or not self.redis:
            return None
        
        return self._search_vector_db(self.cache_idx, prompt, top_k=1, threshold=config.CACHE_THRESHOLD)

    def store_cache(self, prompt: str, response: str):
        """
        Saves a successful Q&A pair for future reuse.
        """
        if not config.ENABLE_CACHE or not self.redis:
            return

        try:
            # Ensure index exists
            self._ensure_index(self.cache_idx)
            
            vector = self.model.encode(prompt).astype(np.float32).tobytes()
            key = f"cache:{hashlib.md5(prompt.encode()).hexdigest()}"
            
            self.redis.hset(key, mapping={
                "prompt": prompt,
                "response": response,
                "vector": vector
            })
        except Exception as e:
            print(f"Cache storage error: {e}")

    def _search_vector_db(self, index: str, prompt: str, top_k: int, threshold: float = 0.0) -> Optional[str]:
        try:
            # Check if index exists
            self.redis.execute_command("FT.INFO", index)
            
            vector = self.model.encode(prompt).astype(np.float32).tobytes()
            
            # Using DIALECT 2 for improved vector search performance
            res = self.redis.execute_command(
                "FT.SEARCH", index,
                f"*=>[KNN {top_k} @vector $vec AS score]",
                "PARAMS", "4", "vec", vector,
                "SORTBY", "score",
                "DIALECT", "2",
                "RETURN", "2", "content", "response"
            )
            
            if res and res[0] > 0:
                # res[0] is count, res[1] is key name, res[2] is fields list
                # Since we return 2 fields, we need to find which one is present
                fields = res[2]
                score = 0.0 # FT.SEARCH with KNN returns distance in a specific way if requested
                
                # Check for content (RAG) or response (Cache)
                field_dict = {fields[i]: fields[i+1] for i in range(0, len(fields), 2)}
                
                # If we have a threshold, we should ideally check the 'score'
                # but Redis KNN distance is 0.0 for exact matches (Cosine).
                # For now, if we get a result from FT.SEARCH KNN, it's the closest.
                if "response" in field_dict:
                    self.hits += 1
                    return field_dict["response"]
                return field_dict.get("content")
                
        except Exception:
            return None
        return None

    def _ensure_index(self, index_name: str):
        try:
            self.redis.execute_command("FT.INFO", index_name)
        except:
            # Create a simple cache index if it doesn't exist
            # Note: We assume 384 dim for all-MiniLM-L6-v2
            dim = 384 
            self.redis.execute_command(
                "FT.CREATE", index_name, "ON", "HASH", "PREFIX", "1", "cache:",
                "SCHEMA", "response", "TEXT", "vector", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32", "DIM", str(dim), "DISTANCE_METRIC", "COSINE"
            )
