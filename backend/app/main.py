from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from dotenv import load_dotenv
from app.db.help_requests import create_help_request, get_request_by_status, get_requests_by_id, update_help_request
from app.db.knowledge_base import add_knowledge, list_knowledge, update_embedding
from app.agent.agent_methods import classify_user_message, find_kb_match, generate_small_talk_response, get_hf_embedding

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class HelpRequest(BaseModel):
    customer_name: str
    question: str

class ChatMessage(BaseModel):
    message: str
    customer_name: str = "Customer"

class SupervisorResponse(BaseModel):
    request_id: str
    answer: str

@app.post("/help-request")
def post_help_request(request: HelpRequest):

    print(f'type of request: {type(request)}')
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
    # db.collection(FIREBASE_HELP_REQUESTS_COLLECTION).document(request_id).set(data)
    create_help_request(data)
    logger.info(f"Help request created: {request.question}")
    return {"status": "pending", "request_id": request_id}

@app.get("/requests")
def list_requests(status: str | None = None, id: str | None = None):
    """View all help requests (optionally filter by status)"""
    if id:
        docs = get_requests_by_id(id)
    elif status:
        docs = get_request_by_status(status)
    else:
        docs = get_request_by_status(None)
    return docs

@app.post("/respond")
def supervisor_respond(response: SupervisorResponse):
    """Supervisor submits an answer"""

    request = get_requests_by_id(response.request_id)[0]
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already resolved")

    request.update({
        "status": "resolved",
        "resolved_at": datetime.now().isoformat(),
        "answer": response.answer
    })
    
    update_help_request(response.request_id, request)

    logger.info(f"Response submitted: {response.answer}")

    # Generate embedding for the Q&A pair
    embedding = get_hf_embedding(request["question"])

    # Update knowledge base
    add_knowledge(request["question"], response.answer, embedding)
    logger.info(f"Knowledge base updated for: '{request['question']}'")

    return {"status": "resolved", "request_id": response.request_id}

@app.get("/knowledge-base")
def get_knowledge():
    return list_knowledge()

@app.post("/ai-respond")
def ai_respond(msg: ChatMessage, background_tasks: BackgroundTasks):
    """
    AI chat endpoint:
    0. LLM classifies the intent
    1. If small-talk → LLM answers directly
    2. If business_query → Try KB first
    3. Else → escalate to supervisor
    """

    try:
        query = msg.message.strip()

        # 0. Let the LLM classify the query
        logger.info(f"Classifying intent...")
        intent = classify_user_message(query)
        logger.info(f"Intent classified as: {intent}")


        # 1. Direct LLM small-talk handling
        if intent == "small_talk":
            logger.info(f"Handling small talk...")
            answer = generate_small_talk_response(query)
            return {
                "response": answer,
                "source": "small_talk"
            }

        
        # 2. Business query → Try KB first
        if intent == "business_query":
            logger.info(f"Handling business query...")
            logger.info(f"Searching knowledge base for query...")
            kb_answer = find_kb_match(query)
            if kb_answer:
                logger.info(f"KB match for business query: '{query}'")
                return {
                    "response": kb_answer,
                    "source": "knowledge_base"
                }

        # 3. Fall back → escalate to supervisor
        req = {
            "id": str(uuid.uuid4()),
            "customer_name": msg.customer_name,
            "question": msg.message,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "resolved_at": None,
            "answer": None
        }
        
        logger.info(f"Escalating to supervisor for query: '{query}'")
        background_tasks.add_task(create_help_request, req)

        return {
            "response": """Your question has been forwarded to the supervisor. They'll reach out to you shortly. 
                        Thank you for your patience! Can I assist you with anything else in the meantime?"""     
        }

    except Exception as e:
        logger.error(f"AI respond error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def preload_kb_embeddings():
    """
    Precompute embeddings for KB entries that don't have them.
    Runs once when application starts.
    """
    kb = list_knowledge()
    if not kb:
        return

    logger.info("🔄 Preloading missing knowledge base embeddings...")

    for item in kb:
        if "embedding" not in item or not item["embedding"]:
            question = item["question"]
            embedding = get_hf_embedding(question)

            # Update Firestore KB entry
            update_embedding(question, embedding)
            logger.info(f"Cached embedding for: {question}")

    logger.info("✅ KB embeddings preloaded.")
