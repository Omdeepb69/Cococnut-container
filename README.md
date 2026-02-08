# 🥥 Project Coconut: The Ultimate AI MLOps Harness

**Project Coconut** is a high-performance, containerized ecosystem designed to transform raw language models into secure, context-aware production services. It bridges the gap between a model file and a professional API by providing a complete infrastructure stack for inference, memory, RAG, and security.

---

## 🏛️ The 5-Layer Design System

Coconut is built on a modular "Modular Armor" architecture, where each layer serves a specific production purpose:

### 1. The Shell (Infrastructure)
*   **Technology**: Docker Compose, Redis Stack 7.4.
*   **Purpose**: Provides the backbone of the system. We use **Redis Stack** not just for caching, but as a high-performance Vector Database and state store.
*   **Feature**: Multi-service orchestration ensures that the API and the Database are always in sync and isolated.

### 2. The Guard (Identity & Security)
*   **Technology**: FastAPI Security, SHA-256 Hashing, Atomic Redis Windows.
*   **Purpose**: Protects your AI from abuse and unauthorized access.
*   **Features**:
    *   **Self-Service Keys**: Generate hashed API keys on the fly.
    *   **Tiered Rate Limiting**: Limit users based on their 'Pro' or 'Free' status.
    *   **Atomic Logic**: Prevents "window leaking" to ensure strict compliance with usage limits.

### 3. The Core (Brain & Memory)
*   **Technology**: Hugging Face Transformers, PyTorch (CPU-Optimized), Redis Lists.
*   **Purpose**: The actual AI engine.
*   **Features**:
    *   **Gonyai-v1 Support**: Native integration with Konkani-language optimized models.
    *   **Sliding Window Memory**: Unlike basic APIs, Coconut remembers the last N messages of a conversation, allowing for natural, multi-turn dialogues.

### 4. The Wisdom (RAG & Knowledge)
*   **Technology**: RediSearch, Sentence-Transformers (`all-MiniLM-L6-v2`).
*   **Purpose**: Grounds the AI in facts to prevent hallucinations.
*   **Features**:
    *   **Semantic Search**: Uses vector embeddings to find the most relevant context for any prompt.
    *   **Dynamic Injection**: Automatically augments user prompts with retrieved knowledge before inference.

### 5. The Factory (MLOps & CI/CD)
*   **Technology**: GitHub Actions, Trivy Security, Prometheus-compatible metrics.
*   **Purpose**: Automates the lifecycle of the AI container.
*   **Features**:
    *   **Auto-Scanning**: Every push triggers a security scan for OS and library vulnerabilities.
    *   **Auto-Publish**: Automatically ships verified images to Docker Hub.
    *   **Observability**: Track latency and inference counts via the `/metrics` endpoint.

---

## 🚀 Installation & Setup

### Prerequisites
*   Ubuntu/Linux (Optimized)
*   Docker & Docker Compose
*   Python 3.9+ (External)

### Step 1: Clone and Launch
```bash
git clone https://github.com/Omdeepb69/Cococnut-container.git
cd coconut
docker compose up --build -d
```

### Step 2: Initialize the Wisdom (RAG)
Inject the knowledge base into the vector index:
```bash
docker compose exec coconut-api python3 ingest.py
```

---

## 📖 Complete Feature Tutorial

### 1. Generating Your First API Key
To interact with the `/chat` endpoint, you need an API key. 
```bash
# Generate a PRO tier key
curl -X POST "http://localhost:8000/generate-key?tier=pro"
```
**Response Schema:**
```json
{
  "api_key": "cc_live_...",
  "tier": "pro",
  "limit": 100,
  "window": 60
}
```

### 2. Performing a RAG-Powered Chat
Ask a question about the system. The API will search Redis for context and ground the response.
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "X-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What is Layer 4 of Coconut?",
       "session_id": "user_session_99"
     }'
```

### 3. Testing Conversation Memory
The `session_id` allows the "Brain" to remember you.
*   **Input 1**: "My name is Omdeep."
*   **Input 2**: "What is my name?" -> **Expected**: "Your name is Omdeep."

### 4. Monitoring the Harness
Access the OTLP-compatible metrics endpoint:
```bash
curl http://localhost:8000/metrics
```
You can see `inference_count`, `last_latency`, and `cache_hits`.

---

## 🛠️ Master Commands Reference

### Docker Management
| Goal | Command |
| :--- | :--- |
| **Start Services** | `docker compose up -d` |
| **Stop & Remove** | `docker compose down` |
| **View API Logs** | `docker compose logs -f coconut-api` |
| **Restart AI Engine** | `docker compose restart coconut-api` |

### Knowledge & Vector DB
| Goal | Command |
| :--- | :--- |
| **Reset Index** | `docker compose exec redis-stack redis-cli FT.DROPINDEX coconut_idx` |
| **View Vector Info** | `docker compose exec redis-stack redis-cli FT.INFO coconut_idx` |
| **Manual Ingest** | `docker compose exec coconut-api python3 ingest.py` |

### Security & Troubleshooting
| Goal | Command |
| :--- | :--- |
| **Check Health** | `curl http://localhost:8000/health` |
| **Inspect Redis** | `docker compose exec redis-stack redis-cli` |
| **Test Rate Limit** | `for i in {1..15}; do curl -X POST http://localhost:8000/chat -H "X-API-Key: YOUR_KEY"; done` |

---

## 🚢 CI/CD Workflow Setup

Your repository is equipped with a professional GitHub Action:

1.  **Code Check**: Triggers on every push to `main`.
2.  **Security Scan**: Runs **Trivy** to find vulnerabilities.
3.  **Docker Push**: If tests and scans pass, it pushes to Docker Hub.

**Required GitHub Secrets:**
- `DOCKERHUB_USERNAME`: Your Docker Hub username.
- `DOCKERHUB_TOKEN`: Your Docker Hub Access Token.

---
*Powered by Project Coconut - Bridging AI and Production.*
