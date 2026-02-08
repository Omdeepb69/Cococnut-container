# 🥥 Project Coconut: The Production-Grade AI Harness

Project Coconut is a professional, modular AI ecosystem designed to turn raw models into production-ready services. It implements a complete 5-layer architecture for secure, context-aware, and observable AI deployments.

---

## 🏗️ The 5-Layer Architecture

Coconut is built on the philosophy of "The Shell, The Guard, The Core, The Wisdom, and The Factory."

1.  **Infrastructure (The Shell)**: Containerized orchestration using Docker Compose and high-performance **Redis Stack** for vector and key-value storage.
2.  **Identity & Security (The Guard)**: Secure API Key management using SHA-256 hashing and **Atomic Rate Limiting** to prevent usage leaks.
3.  **Brain & Memory (The Core)**: Integration with the **omdeep22/Gonyai-v1** model featuring a sliding-window memory system to maintain conversation flow.
4.  **RAG & Knowledge (The Wisdom)**: Deep semantic retrieval using **Redis Vector Search** and `sentence-transformers` for fact-grounded responses.
5.  **MLOps & CI/CD (The Factory)**: Automated build pipelines with **GitHub Actions**, vulnerability scanning with **Trivy**, and real-time observability via `/metrics`.

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for ingestion scripts)

### 2. Launch the Stack
```bash
# Start the API and Vector DB
docker compose up --build -d
```

### 3. Initialize Knowledge (RAG)
Inject the initial facts into the vector database:
```bash
docker compose exec coconut-api python3 ingest.py
```

---

## 📖 Tutorial: Using the Harness

### 🔐 Step 1: Generate an API Key
Coconut doesn't use raw passwords. Generate a secure, hashed key:
```bash
# Tiers: free or pro
curl -X POST "http://localhost:8000/generate-key?tier=pro"
```
**Important**: Save the `api_key` shown. It is hashed immediately and cannot be recovered if lost.

### 🧠 Step 2: Chat with Context
Ask a question. Coconut will search its "Knowledge" (RAG) and "Memory" before responding:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "X-API-Key: YOUR_GENERATED_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What are the 5 layers of Project Coconut?",
       "session_id": "tutorial_user_01"
     }'
```

### 📊 Step 3: Monitor Performance
Check how many inferences have been made and the health of the cache:
```bash
curl http://localhost:8000/metrics
```

---

## 🧪 Testing Before Publishing

Before you `docker push`, verify the stack integrity with these commands:

| Test Item | Command | Expected Result |
| :--- | :--- | :--- |
| **Security** | `curl -I -X POST http://localhost:8000/chat` | `401 Unauthorized` |
| **Rate Limit** | Run a loop of 11 requests with a `free` key | Request 11 should return `429` |
| **RAG** | Ask "What is Layer 4?" | Response should mention "The Wisdom" or "Vector Search" |
| **Memory** | Say "My name is Coconut", then ask "What is my name?" | Response should remember "Coconut" |

---

## 🚢 Publishing to your Repo

1.  **Tag the image**:
    ```bash
    docker tag coconut-coconut-api your_dockerhub_user/coconut:v1.0
    ```
2.  **Push to the cloud**:
    ```bash
    docker push your_dockerhub_user/coconut:v1.0
    ```

---

## 🛠️ Maintenance & Cleanup
- **Clear Vectors**: `redis-cli -p 6380 FT.DROPINDEX coconut_idx`
- **Reset Usage**: `redis-cli -p 6380 DEL usage:<hashed_key>`

---
*Created with ❤️ by the Project Coconut Team.*
