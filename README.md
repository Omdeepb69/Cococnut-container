# 🥥 Project Coconut: The S-Tier AI MLOps Harness (v1.1.0)

**Project Coconut** is a professional, modular AI ecosystem designed for high-performance production deployments. It bridges the gap between raw models and scalable services with its unique 5-layer architecture.

---

## 🏛️ S-Tier Architecture (The "Modular Armor")

1.  **Hardware Auto-Sensing**: Automatically detects NVIDIA GPUs and applies FP16 precision. Falls back to optimized FP32 on CPUs.
2.  **Semantic Inference Cache**: Verified **99% latency reduction** for repeat queries. Responds in <1s by reusing previous model logic.
3.  **Dynamic Feature Toggles**: Enable/Disable RAG, Semantic Caching, and Session Memory instantly via environment variables.
4.  **Auto-MLOps (CI/CD)**: Integrated **GitHub Actions** with **Trivy** security scanning and automated Docker Hub deployment.

---

## 🚀 The S-Tier Setup Workflow (Step-by-Step)

Follow this exact sequence to go from a clean server to a production-ready AI backend.

### Step 1: Initialize the Stack

**Option A: Local Build (Developer Mode)**
```bash
git clone https://github.com/Omdeepb69/Cococnut-container.git
cd coconut
docker compose up --build -d
```

**Option B: Docker Cloud (Production Mode)**
```bash
# Pull the pre-built S-Tier image
docker pull omdeep22/coconut_can:latest
```

### Step 2: Establish Identity (Generate API Key)
The API is locked by default. Generate your first production key:
```bash
# This creates a 'pro' tier key with 100 req/min limit
curl -X POST "http://localhost:8000/generate-key?tier=pro"
```
> [!IMPORTANT]
> Save the returned `api_key` immediately. It is hashed for security and cannot be shown again.

---

## 🐋 Docker Registry: The "Coconut Can" Deep Dive

If you are using the image `omdeep22/coconut_can` without the full repository, use these commands to control the engine.

### 1. Simple Run (Standalone)
```bash
# Start a Redis dependency first
docker run -d --name redis-brain -p 6380:6379 redis/redis-stack:latest

# Launch the Coconut Can
docker run -d \
  --name coconut-engine \
  -p 8000:8000 \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6380 \
  omdeep22/coconut_can:latest
```

### 2. Full Ingestion (Adding Data)
```bash
# Run ingestion inside the active container
docker exec -it coconut-engine python3 ingest.py "The secret verification code is COCO-99."
```

### 3. Hardware Acceleration (NVIDIA GPU)
```bash
docker run -d \
  --name coconut-gpu \
  --gpus all \
  -p 8000:8000 \
  -e DEVICE=cuda \
  omdeep22/coconut_can:latest
```

### 4. System Maintenance & Log Monitoring
| Task | Command |
| :--- | :--- |
| **Follow Live AI Logic** | `docker logs -f coconut-engine` |
| **Check Resource Usage** | `docker stats coconut-engine` |
| **Enter Shell (Debug)** | `docker exec -it coconut-engine bash` |
| **Inspect Env Config** | `docker inspect coconut-engine | grep -A 20 "Env"` |
| **Reset Knowledge** | `docker exec redis-stack redis-cli FT.DROPINDEX coconut_idx` |
| **Clear Logic Cache** | `docker exec redis-stack redis-cli FT.DROPINDEX coconut_cache_idx` |
| **Debug Auth Keys** | `docker exec redis-stack redis-cli KEYS "api_key:*"` |
| **Clean Deep Exit** | `docker system prune -a --volumes` |

---

## 🛠️ How to "Edit Setup" (Configuration)

Project Coconut is designed to be modified without changing code. You can inject these as environment variables (`-e`).

### 1. Changing the AI Model
To swap the "Brain", set the `MODEL_ID`:
```bash
docker run -e MODEL_ID=gpt2 omdeep22/coconut_can:latest
```

### 2. Toggling Production Features
- `ENABLE_RAG=False`: Disables knowledge lookup.
- `ENABLE_CACHE=False`: Disables semantic reuse (forces fresh AI generation every time).
- `ENABLE_MEMORY=False`: Disables session history.
- `CACHE_THRESHOLD=0.90`: Makes the semantic cache harder to hit (for more precise matches).

---

## 📈 Performance & Scaling

- **Cold Start (CPU)**: ~160s
- **Hot Cache (Reuse)**: **< 1s**

### 🌐 Advanced Production Guides
- [Scaling to 1 Million Users](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/scaling_guide.md)
- [CI/CD Pipeline Tutorial](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/ci_cd_tutorial.md)

---
*Created with ❤️ by the Project Coconut Team.*
