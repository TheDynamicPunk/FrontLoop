from app.db.firebase_client import db

KB_COLLECTION = "knowledge_base"

def add_knowledge(question: str, answer: str, embedding: list[float]):
    db.collection(KB_COLLECTION).document(question.lower().strip()).set({
        "question": question.lower().strip(),
        "answer": answer.strip(),
        "embedding": embedding
    })

def update_embedding(question: str, embedding: list[float]):
    doc_ref = db.collection(KB_COLLECTION).document(question.lower().strip())
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"embedding": embedding})

def get_answer(question: str):
    doc = db.collection(KB_COLLECTION).document(question.lower().strip()).get()
    return doc.to_dict()["answer"] if doc.exists else None

def list_knowledge():
    docs = db.collection(KB_COLLECTION).stream()
    return [doc.to_dict() for doc in docs]
