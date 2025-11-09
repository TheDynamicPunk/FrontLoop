import requests
from livekit import rtc
import asyncio

KNOWN_ANSWERS = {
    "what are your working hours": "We're open from 9 AM to 7 PM every day.",
    "where are you located": "We're at 123 Front Street, Bangalore.",
    "do you take walk-ins": "Yes, we do accept walk-in customers!"
}

async def handle_call(question: str):
    # Normalize question
    q = question.strip().lower()

    if q in KNOWN_ANSWERS:
        print(f"[AI]: {KNOWN_ANSWERS[q]}")
    else:
        print(f"[AI]: Hmm, let me check with my supervisor and get back to you.")
        await request_help(question)

async def request_help(question: str):
    data = {
        "customer_name": "Jane Doe",  # Simulated caller
        "question": question
    }
    try:
        response = requests.post("http://localhost:8000/help-request", json=data)
        if response.status_code == 200:
            print(f"[HELP REQUEST SENT] {response.json()}")
        else:
            print(f"[ERROR] Failed to send help request: {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION] Could not contact backend: {e}")

async def simulate_incoming_call():
    print("📞 Incoming simulated call...")
    while True:
        question = input("👤 Customer: ")
        await handle_call(question)

if __name__ == "__main__":
    asyncio.run(simulate_incoming_call())
