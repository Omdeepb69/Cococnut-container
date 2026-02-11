# 🥥 Project Coconut: The S-Tier AI MLOps Harness (v1.1.0)

[![Hugging Face Model](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model-yellow)](https://huggingface.co/omdeep22/Gonyai-v1)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/omdeep22/Konkani_books_corpus-v2)
[![Docker Hub](https://img.shields.io/badge/Docker-Hub-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/omdeep22/coconut_can)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Author: Omdeepb69](https://img.shields.io/badge/GitHub-Omdeepb69-black)](https://github.com/Omdeepb69)

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

### Step 4: Verify the Pipeline
```bash
# Replace YOUR_KEY with the key from Step 2
curl -X POST "http://localhost:8000/chat" \
     -H "X-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is Project Coconut?", "session_id": "init_test"}'
```

---

## 🧩 Universal Model Compatibility

Project Coconut's S-Tier Engine is built on the industry-standard `AutoModelForCausalLM` and `AutoTokenizer` frameworks. This means you can swap the "Brain" with **almost any model on Hugging Face** simply by changing the `MODEL_ID`.

### Supported Model Families
- **Mistral / Mixtral**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Llama 3 / 2**: `meta-llama/Meta-Llama-3-8B-Instruct`
- **Gemma**: `google/gemma-7b-it`
- **Falcon**: `tiiuae/falcon-7b-instruct`
- **GPT-2 / Neo**: `gpt2` (Great for low-resource testing)

### How it works?
The harness uses `apply_chat_template`, which automatically detects and applies the correct prompt format (System/User/Assistant) for whichever model you choose. No manual prompt engineering required!

> [!TIP]
> **Resource Planning**: Large models (7B+ parameters) require significant VRAM/RAM. Ensure your server has 16GB+ RAM for 7B models on CPU, or 24GB+ VRAM for GPU deployment.

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

### 3. Hardware Maximizer: 4/8-bit Quantization
Run 7B+ models on consumer GPUs (T4, 3060) by enabling quantization:
```bash
docker run -e LOAD_IN_4BIT=True omdeep22/coconut_can
```

### 4. Production UX: Real-Time Streaming
Use the new streaming endpoint for a high-end, typing-effect UI:
```bash
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello Gonyai!"}'
```

---

## ☸️ S-Tier Kubernetes Scaling (1M+ Users)

For hyper-scale deployments, use the provided Kubernetes manifests to orchestrate a resilient cluster.

### 1. Unified Deployment
Apply all manifests in the `k8s/` directory to launch the API, Redis cluster, and Auto-scaler:
```bash
kubectl apply -f k8s/
```

### 2. Manual Scaling (Emergency)
If traffic spikes beyond the HPA's reaction time, scale manually:
```bash
kubectl scale deployment coconut-api --replicas=50
```

### 3. Monitoring the Cluster
- **Pods Status**: `kubectl get pods -l app=coconut`
- **Auto-scaling events**: `kubectl get hpa coconut-hpa`
- **Service URL**: `kubectl get svc coconut-service`

### 🛡️ Deployment Security (Crucial)
For production, you **must** set an admin key to control key generation:
- **Docker**: `docker run -e ADMIN_ROOT_KEY="secret" omdeep22/coconut`
- **K8s**: Edit and apply `k8s/secrets.yaml` before deployment.

---

## 📈 Performance & Scaling

- **Cold Start (CPU)**: ~160s
- **Hot Cache (Reuse)**: **< 1s**

### 🌐 Advanced Production Guides
- [Scaling to 1 Million Users](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/scaling_guide.md)
- [CI/CD Pipeline Tutorial](file:///home/omdeep-borkar/.gemini/antigravity/brain/9f6d224a-9043-46d6-a450-a3e2bc1abf41/ci_cd_tutorial.md)

---
**Created with ❤️ by** [![Author: Omdeepb69](https://img.shields.io/badge/GitHub-Omdeepb69-black)](https://github.com/Omdeepb69)

