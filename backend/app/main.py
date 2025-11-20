from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import uuid
from app.db.firebase_client import db
from app.db.knowledge_base import add_knowledge, list_knowledge

app = FastAPI(title="FrontLoop Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://frontloop-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HELP_REQUESTS_COLLECTION = "help_requests"

class HelpRequest(BaseModel):
    customer_name: str
    question: str

class SupervisorResponse(BaseModel):
    request_id: str
    answer: str

@app.post("/help-request")
def create_help_request(request: HelpRequest):
    request_id = str(uuid.uuid4())
    data = {
        "id": request_id,
        "customer_name": request.customer_name,
        "question": request.question,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "resolved_at": None,
        "answer": None
    }
    db.collection(HELP_REQUESTS_COLLECTION).document(request_id).set(data)
    print(f"[SUPERVISOR NOTIFY] Need help answering: '{request.question}'")
    return {"status": "pending", "request_id": request_id}

@app.get("/requests")
def list_requests(status: str | None = None, id: str | None = None):
    """View all help requests (optionally filter by status)"""
    collection = db.collection(HELP_REQUESTS_COLLECTION)
    if status:
        docs = collection.where("status", "==", status).stream()
    elif id:
        docs = collection.where("id", "==", id).stream()
    else:
        docs = collection.stream()
    return [doc.to_dict() for doc in docs]

@app.post("/respond")
def supervisor_respond(response: SupervisorResponse):
    """Supervisor submits an answer"""
    doc_ref = db.collection(HELP_REQUESTS_COLLECTION).document(response.request_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Request not found")

    data = doc.to_dict()
    if data["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already resolved")

    data.update({
        "status": "resolved",
        "resolved_at": datetime.now().isoformat(),
        "answer": response.answer
    })
    doc_ref.update(data)

    print(f"[AI FOLLOW-UP] Hi again! {response.answer}")
    print(f"[KB UPDATE] Learned new answer for: '{data['question']}'")

    # Update knowledge base
    add_knowledge(data["question"], response.answer)

    return {"status": "resolved", "request_id": response.request_id}

@app.get("/knowledge-base")
def get_knowledge():
    return list_knowledge()

@app.get("/health")
def health_check():
    return {"status": "ok"}