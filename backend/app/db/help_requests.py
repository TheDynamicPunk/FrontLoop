from app.db.firebase_client import db

HELP_REQUESTS_COLLECTION = "help_requests"

def get_requests_by_id(id: str | None = None):
    doc = db.collection(HELP_REQUESTS_COLLECTION).document(id).get()

    return [doc.to_dict()] if doc.exists else []

def get_request_by_status(status: str | None = None):
    collection = db.collection(HELP_REQUESTS_COLLECTION)

    if status:
        docs = collection.where("status", "==", status).stream()
    else:
        # no status provided → return all docs
        docs = collection.stream()

    return [doc.to_dict() for doc in docs]

def create_help_request(data: dict):
    print(f'Creating help request with data...')
    doc_ref = db.collection(HELP_REQUESTS_COLLECTION).document(data["id"])
    doc_ref.set(data)

def update_help_request(id: str, data: dict):
    doc_ref = db.collection(HELP_REQUESTS_COLLECTION).document(id)
    doc_ref.update(data)