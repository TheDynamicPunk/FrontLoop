# 🧠 FrontLoop – Human-in-the-Loop AI Supervisor

FrontLoop is a lightweight prototype demonstrating a **human-supervised AI agent system**.  
When the AI doesn’t know an answer during a customer call, it **escalates to a human supervisor**, follows up automatically, and **learns** from the response.

---

## Architecture Overview

**Modules:**
1. **AI Agent (simulated via LiveKit)** – handles incoming calls and triggers help requests.
2. **Backend (FastAPI)** – manages help requests, supervisor responses, and knowledge base updates.
3. **Frontend (React + Tailwind)** – internal dashboard for supervisors to view and respond to pending requests.

**Flow:**
Caller → AI Agent → Help Request → Supervisor UI → Response → Knowledge Base → AI learns

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI (Python), Firebase / SQLite |
| Frontend | React + Tailwind CSS |
| AI Simulation | LiveKit SDK |
| DB | Firebase or SQLite (local) |
| Deployment | Local run (demo-ready) |

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

- AI escalation flow (simulated call → help request)

- Supervisor dashboard (view/respond requests)

- Knowledge base auto-update and persistence

- Lifecycle tracking: Pending → Resolved / Unresolved

- Timeout handling and logs

## Design Decisions

- Decoupled services – allows easy scaling and maintainability.

- Simple data model – designed for clarity and traceability.

- Local-first – works without external APIs for easy testing.

- Extendable – Phase 2 can easily add real-time supervisor interaction.


### Run Commands
```pwsh
uvicorn main:app --reload
streamlit run backend/supervisor_dashboard.py
```