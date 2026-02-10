from redis import Redis
import json

class ConversationMemory:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour expiration for sessions

    def _get_key(self, session_id: str) -> str:
        return f"chat:history:{session_id}"

    def add_message(self, session_id: str, role: str, content: str):
        if not self.redis:
            return
            
        key = self._get_key(session_id)
        message = json.dumps({"role": role, "content": content})
        
        # Push to the right (end) of the list
        self.redis.rpush(key, message)
        
        # Trim to keep last 15 messages (Sliding Window)
        # LLM Context protection: prevents session overflow
        self.redis.ltrim(key, -15, -1)
        
        # Refresh TTL
        self.redis.expire(key, self.ttl)

    def get_history(self, session_id: str) -> list:
        if not self.redis:
            return []
            
        key = self._get_key(session_id)
        messages_raw = self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in messages_raw]
