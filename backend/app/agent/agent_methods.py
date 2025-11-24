import os
import requests
import logging
import numpy as np
from dotenv import load_dotenv
from ollama import Client

from app.db.knowledge_base import list_knowledge

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face configuration (for embeddings)
HF_API_KEY = os.getenv("HF_API_KEY", "")
KB_MATCH_THRESHOLD = os.getenv("KB_MATCH_THRESHOLD", 0.59)

# Ollama configuration (for LLM chat only)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.com")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")

ollama_client = Client(
    host=OLLAMA_HOST,
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'} if OLLAMA_API_KEY else {}
)

def classify_user_message(query: str) -> str:
    """
    Uses the LLM to classify the user query into:
      - small_talk
      - business_query
      - supervisor_needed
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intent classification engine. "
                    "Given a user query, classify it into one of: "
                    " - small_talk: greetings, chit-chat, casual conversation. "
                    " - business_query: questions about services, prices, appointments, troubleshooting. "
                    " - supervisor_needed: anything unclear, confusing, or that requires human review. "
                    "Respond ONLY with one of these labels. No explanations."
                )
            },
            {"role": "user", "content": query}
        ]

        response_text = ""
        for part in ollama_client.chat(OLLAMA_MODEL, messages=messages, stream=True):
            response_text += part["message"]["content"].strip()

        return response_text.lower()

    except Exception as e:
        logger.error(f"Message classification error: {e}")
        return "supervisor_needed"

def generate_small_talk_response(query: str):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly assistant. Respond casually and helpfully."
                    "Don't forget that you work for a salon business."
                    "Your responses should always adhere to professional and polite language."
                    "Your responses should always circle back to salon-related topics where possible."
                    "Keep answers brief (under 30 words)."
                )
            },
            {"role": "user", "content": query}
        ]

        resp = ""
        for part in ollama_client.chat(OLLAMA_MODEL, messages=messages, stream=True):
            resp += part["message"]["content"]

        return resp

    except Exception as e:
        logger.error(f"Small-talk generation error: {e}")
        return "Hello! How can I help you today?"


def get_hf_embedding(text: str) -> list:
    """Get embedding from Hugging Face Inference API (router)"""
    if not HF_API_KEY:
        raise RuntimeError("HF_API_KEY not set.")

    url = os.getenv("HF_INFERENCE_MODEL_URL", "")

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"inputs": text}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Hugging Face API error: {response.status_code} {response.text}"
        )

    embedding = response.json()

    # Some models return [[...]]
    if isinstance(embedding, list) and isinstance(embedding[0], list):
        embedding = embedding[0]

    return embedding

def find_kb_match(query: str):
    """Find KB match using semantic search with Hugging Face embeddings"""
    try:
        kb = list_knowledge()
        if not kb:
            return None
        # Get embedding for query
        query_embedding = get_hf_embedding(query)
        best_score = 0
        best_answer = None
        for item in kb:
            kb_embedding = get_hf_embedding(item["question"])
            # Cosine similarity
            score = np.dot(query_embedding, kb_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(kb_embedding)
            )
            if score > best_score and score >= KB_MATCH_THRESHOLD:
                best_score = score
                best_answer = item["answer"]

        logging.info(f"KB match score: {best_score} for query: '{query}'")
        return best_answer
    except Exception as e:
        logger.error(f"KB match error: {e}")
        return None
    
def generate_llm_response(query: str):
    """Generate response using Ollama LLM"""
    try:
        messages = [
            {
                'role': 'system',
                'content': 'You are a helpful AI assistant for a salon business. Answer customer questions professionally and concisely. Keep answers under 200 words.'
            },
            {
                'role': 'user',
                'content': query
            }
        ]
        
        print(f"Generating LLM response for query: '{query}' using Ollama model '{OLLAMA_MODEL}'")
        response_text = ""
        for part in ollama_client.chat(OLLAMA_MODEL, messages=messages, stream=True):
            print(f"Received part: {part['message']['content']}")
            response_text += part['message']['content']
        
        print(f"LLM response: '{response_text}'")
        return response_text
    except Exception as e:
        logger.error(f"LLM generation error: {e}")
        return None