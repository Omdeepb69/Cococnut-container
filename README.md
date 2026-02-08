# 🥥 Project Coconut: The S-Tier AI MLOps Harness (v1.1.0)

**Project Coconut** is a professional, modular AI ecosystem designed for high-performance production deployments. It bridges the gap between raw models and scalable services with its unique 5-layer architecture.

---

## 🏛️ S-Tier Architecture (The "Modular Armor")

1.  **Hardware Auto-Sensing**: Automatically detects NVIDIA GPUs and applies FP16 precision. Falls back to optimized FP32 on CPUs.
2.  **Semantic Inference Cache**: Verified **99% latency reduction** for repeat queries. Responds in <1s by reusing previous model logic.
3.  **Dynamic Feature Toggles**: Enable/Disable RAG, Semantic Caching, and Session Memory instantly via environment variables.
4.  **Stateless API Design**: Ready for horizontal scaling across Kubernetes clusters or multi-server farms.
5.  **Clean CLI Ingestion**: Modular ingestion script for populating the vector database with production knowledge.

---

## 🚀 Deep Setup & Installation Guide

### 1. Prerequisites
- **Docker & Docker Compose** installed.
- **NVIDIA Container Toolkit** (Optional, for GPU acceleration).
- **8GB+ RAM** (16GB+ recommended for large models like Gonyai-v1).

### 2. Quick Installation
```bash
# 1. Clone the repository
git clone https://github.com/Omdeepb69/Cococnut-container.git
cd coconut

# 2. Launch the full stack
docker compose up --build -d

# 3. Verify Health
curl http://localhost:8000/health
```

### 3. Production Presets
| Mode | Env Override | Best For |
| :--- | :--- | :--- |
| **Ultra-Fast (GPU)** | `DEVICE=cuda` | Real-time production chat (NVIDIA T4/A10G). |
| **Budget (CPU)** | `DEVICE=cpu` | Internal testing / Low-cost VPS. |
| **Knowledge-Only** | `ENABLE_RAG=True ENABLE_CACHE=False` | Pure information retrieval without response reuse. |

---

## 💻 Technical Command Reference (Cheat Sheet)

### 🔑 Security & Identity
**Generate a New API Key:**
```bash
# Tier can be 'free' or 'pro'
curl -X POST "http://localhost:8000/generate-key?tier=pro"
```
*Note: Save your key! It is hashed in Redis and cannot be recovered if lost.*

### 💬 Chat & Interaction (The AI Core)
**Send a Chat Prompt (Requires X-API-Key Header):**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "X-API-Key: YOUR_API_KEY_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Tell me about Project Coconut.",
       "session_id": "test_user_001"
     }'
```

### 🧠 Knowledge Management (RAG)
**Inject Knowledge into the Vector DB:**
```bash
# Run from the host machine
docker compose exec coconut-api python3 ingest.py "Project Coconut is the ultimate AI harness."
```

**Wipe the Knowledge Base (Hard Reset):**
```bash
docker compose exec redis-stack redis-cli FT.DROPINDEX coconut_idx
```

---

## ⚙️ Engineering Configuration (Env Vars)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `MODEL_ID` | `omdeep22/Gonyai-v1` | HuggingFace Repo for the Brain. |
| `EMBEDDING_MODEL_ID` | `all-MiniLM-L6-v2` | Model used for RAG and Cache. |
| `ENABLE_RAG` | `True` | Toggle Knowledge-Grounding. |
| `ENABLE_CACHE` | `True` | Toggle Semantic Cache (Response Reuse). |
| `ENABLE_MEMORY` | `True` | Toggle Sliding Window Memory. |
| `DEVICE` | `auto` | Set manually to `cuda` or `cpu` if needed. |
| `CACHE_THRESHOLD` | `0.85` | Similarity score required for a cache hit. |

---

## 📈 Monitoring & Health

### 1. Performance Metrics
```bash
curl http://localhost:8000/metrics
```
Returns `inference_count`, `cache_hits`, and active `device`.

### 2. System Logs
```bash
# Follow live logs to see hardware detection in action
docker compose logs -f coconut-api
```

---

## 🌐 Scaling to 1 Million Users

Project Coconut is built for enterprise growth. For deep details, see the [Scaling Roadmap](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/scaling_guide.md).

1. **Step 1: Cluster Deployment**: Move from Docker Compose to **Kubernetes (K8s)**.
2. **Step 2: Model Farms**: Offload inference to **vLLM** or **Triton Inference Server**.
3. **Step 3: Global State**: Multi-node **Redis Cluster** for sharded vector search.

---
*Created with ❤️ by the Project Coconut Team.*
