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

## 🚀 Getting Started

### 1. Zero-Config Launch
```bash
# Clone and start the stack
git clone https://github.com/Omdeepb69/Cococnut-container.git
cd coconut
docker compose up --build -d
```

### 2. Ingest Custom Knowledge (RAG)
```bash
# Ingest facts specifically into the vector index
docker compose exec coconut-api python3 ingest.py "Project Coconut is an S-Tier AI harness by Omdeep."
```

### 3. Generate a Production Key
```bash
curl -X POST "http://localhost:8000/generate-key?tier=pro"
```

---

## 💻 Technical Command Reference

### Docker Orchestration
| Command | Purpose |
| :--- | :--- |
| `docker compose up -d` | Start the API and Redis stack in background. |
| `docker compose build` | Rebuild the API image (after code changes). |
| `docker compose logs -f` | Follow live server logs (useful for hardware detection). |
| `docker compose down` | Stop and remove all containers. |

### CLI Tools (Inside Container)
| Command | Purpose |
| :--- | :--- |
| `python3 ingest.py "text"` | Manually add knowledge to the Vector DB for RAG. |
| `python3 security.py` | (Utility) Internal hashing and key validation. |

### REST API Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/chat` | `POST` | Primary AI interface (requires `X-API-Key`). |
| `/metrics` | `GET` | View inference counts and cache hit rates. |
| `/health` | `GET` | System and Redis connectivity status. |
| `/generate-key` | `POST` | Create a new `free` or `pro` API key. |

---

## ⚙️ Configuration (Environment Variables)

Customize your harness without touching a single line of code:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `MODEL_ID` | `omdeep22/Gonyai-v1` | HuggingFace Repo for the Brain. |
| `EMBEDDING_MODEL_ID` | `all-MiniLM-L6-v2` | Model used for RAG and Cache. |
| `ENABLE_RAG` | `True` | Toggle Knowledge-Grounding. |
| `ENABLE_CACHE` | `True` | Toggle Semantic Cache (Response Reuse). |
| `ENABLE_MEMORY` | `True` | Toggle Sliding Window Memory. |
| `DEVICE` | `auto` | Set manually to `cuda` or `cpu` if needed. |

---

## 📈 Performance & Scaling

### Verified Metrics
- **Initial Request**: ~160s (Generation on CPU).
- **Secondary Request**: **~0.4s (Instant Cache Hit)**.

### 🌐 Scaling to 1 Million Users
Project Coconut is built for enterprise growth. For deep details, see the [Scaling Roadmap](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/scaling_guide.md).

1. **Phase 1: Horizontal API Scaling**
   Deploy 100+ stateless `coconut-api` containers behind a Load Balancer (K8s/ECS).

2. **Phase 2: Decoupled Inference**
   Move the Model Engine to a dedicated "Model Farm" using **vLLM** or **Nvidia Triton** to avoid redundant VRAM usage.

3. **Phase 3: Redis Cluster Clustering**
   Distribute the Semantic Cache and Vector DB across a multi-node Redis cluster for sub-millisecond global orchestration.

---

## 🛠️ Maintenance Reference
- **Check Metrics**: `curl http://localhost:8000/metrics`
- **Clear Vectors**: `redis-cli -p 6380 FT.DROPINDEX coconut_idx`
- **Clear Cache**: `redis-cli -p 6380 FT.DROPINDEX coconut_cache_idx`
- **View Health**: `curl http://localhost:8000/health`

---
*Created with ❤️ by the Project Coconut Team.*
