# 🧠 FrontLoop – Human-in-the-Loop AI Supervisor

FrontLoop is a lightweight prototype demonstrating a **human-supervised AI agent system**.  
When the AI doesn’t know an answer during a customer session, it **escalates to a human supervisor**, follows up automatically, and **learns** from the response.

### Experience [Frontloop](https://frontloop-frontend.onrender.com)

---

## Architecture Overview

**Modules:**
1. **AI Agent Functions (uses ollama cloud and hugging face inference model)** – handles incoming messages, processes them and triggers help requests if unknown.
2. **Backend (FastAPI)** – manages help requests, supervisor responses, and knowledge base updates.
3. **Frontend (React + Tailwind)** – dashboard for supervisors to view and respond to pending requests.

**Flow:**
Client → AI Agent → Help Request → Supervisor UI → Response → Knowledge Base → AI learns

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI (Python), Firebase |
| Frontend | React + Tailwind CSS |
| AI Simulation | Ollama cloud/Hugging Face |
| DB | Firebase |
| Deployment | Render free tier |

---

## ⚙️ Setup Instructions

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm start
```
```
Frontend runs on http://localhost:3000

Backend runs on http://localhost:8000
```

## Key Features

- LLM as a router implementation (LLM categorises user query into small_talk, business_query, supervisor_needed)

- Route based on category
  - small_talk - LLM answers based on system prompt
  - business_query - Run HF embedding model → find in knowledge base → if present return else escalate to supervisor
  - supervisor_needed - Directly escalate to supervisor (human in the loop)

- Supervisor dashboard (view/respond requests)

- Knowledge base auto-update and persistence

- Lifecycle tracking: Pending → Resolved / Unresolved

- Timeout handling and logs
