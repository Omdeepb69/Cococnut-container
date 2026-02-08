import numpy as np
import hashlib
from redis import Redis

INDEX_NAME = "coconut_idx"
VECTOR_DIM = 384 # all-MiniLM-L6-v2 dimension

class SemanticCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self._model = None
        self.hits = 0

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print("Loading embedding model in Cache...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

    def search(self, prompt: str, top_k: int = 1) -> str:
        """
        Searches the vector database for relevant context.
        """
        if not self.redis:
            return None

        try:
            # Check if index exists
            try:
                self.redis.execute_command("FT.INFO", INDEX_NAME)
            except:
                return None

            # Get real embedding
            vector = self.model.encode(prompt).astype(np.float32).tobytes()
            
            # Execute Raw Command
            res = self.redis.execute_command(
                "FT.SEARCH", INDEX_NAME,
                f"*=>[KNN {top_k} @vector $vec AS score]",
                "PARAMS", "4", "vec", vector,
                "SORTBY", "score",
                "DIALECT", "2",
                "RETURN", "1", "content"
            )
            
            if res and res[0] > 0:
                fields = res[2]
                for i in range(0, len(fields), 2):
                    if fields[i] == "content":
                        self.hits += 1
                        return fields[i+1]
            
        except Exception as e:
            print(f"Cache search error: {e}")
            
        return None

    def store(self, prompt: str, response: str):
        pass
