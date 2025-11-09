from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="FrontLoop Backend")

# In-memory store for now (we’ll replace this with a DB later)
HELP_REQUESTS = []

class HelpRequest(BaseModel):
    customer_name: str
    question: str

@app.post("/help-request")
def create_help_request(request: HelpRequest):
    request_id = str(uuid.uuid4())
    new_request = {
        "id": request_id,
        "customer_name": request.customer_name,
        "question": request.question,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    HELP_REQUESTS.append(new_request)

    print(f"[SUPERVISOR NOTIFY] Need help answering: '{request.question}'")

    return {"status": "pending", "request_id": request_id}
