import os
import requests
import asyncio
from dotenv import load_dotenv
import numpy as np

from livekit.agents import AgentSession, Agent, cli, WorkerOptions, JobContext
from livekit.plugins import openai
from livekit.agents.llm import function_tool
from livekit.plugins import silero

from app.db.knowledge_base import list_knowledge

from openai import OpenAI

import logging

logger = logging.getLogger("livekit_agent")
logger.setLevel(logging.INFO)

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

kb = ""

class FrontLoopAgent(Agent):
    def __init__(self):
        global kb 
        kb = list_knowledge()
        super().__init__(
            instructions=(
                """You are an AI virtual assistant for a salon business.
                Answer customer questions using the knowledge base when possible.
                Respond to salutations with a friendly greeting.
                If the knowledge base does not have an answer, do NOT invent one.
                Instead say "Let me check..." and call the `handle_message` function.
                Always be polite and professional.
                """
            ),
            llm="openai/gpt-4o",
        )

    def _find_best_kb_match(self, query: str, threshold: float = 0.70):
        """Use Ollama embeddings for semantic search."""
        client = OpenAI(
            api_key="ollama",  # Dummy key for local Ollama
            base_url="http://localhost:11434/v1"
        )
        
        global kb
        kb = list_knowledge()
        
        if not kb:
            return None
        
        try:
            # Get embedding for customer's question using Ollama
            query_embedding = client.embeddings.create(
                model="nomic-embed-text",  # Free Ollama embedding model
                input=query
            ).data[0].embedding
            
            # Compare with all KB entries
            best_score = 0
            best_answer = None
            
            for item in kb:
                kb_embedding = client.embeddings.create(
                    model="nomic-embed-text",
                    input=item["question"]
                ).data[0].embedding
                
                # Cosine similarity
                score = np.dot(query_embedding, kb_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(kb_embedding)
                )
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_answer = item["answer"]
            
            # logger.info(f"[SEMANTIC MATCH] Score: {best_score:.2f}")
            return best_answer
        except Exception as e:
            logger.error(f"[EMBEDDING ERROR]: {e}")
        
        return None

    async def on_enter(self):
        await self.session.say(text="Hello! How can I help you today?")

    async def on_message(self, text: str):
        await self.handle_message(text)

    @function_tool
    async def handle_message(self, text: str):
        # logger.info(f"[CALLER ASKED]: {text}")
        query = text.strip().lower()

        # Try semantic matching first
        answer = self._find_best_kb_match(query, threshold=0.77)

        if answer:
            logger.info("[AI ANSWERING from KB]")
            await self.session.say(answer)
            return

        # No KB match → escalate
        logger.info("[AI ESCALATING]")
        await self.session.say("Let me check with my supervisor and get back to you.")
        response = await self._send_help_request(query)
        request_id = response['request_id']

        start_time = asyncio.get_event_loop().time()
        timeout = 30 # seconds
        
        while True:
            try:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.warning("[POLLING TIMEOUT] No response after 15 seconds")
                    await self.session.say("I'm sorry, my supervisor is currently unavailable. Could you please try again later?")
                    break
            
                response = requests.get(f"{BACKEND_URL}/requests?id={request_id}")

                if response.status_code == 200:
                    data = response.json()
                    # logger.info(f"[POLLING RESPONSE]: {data[0]['status']}")
                    if data[0].get("answer"):
                        # logger.info(f"[HELP RESPONSE RECEIVED]: {data[0]['answer']}")
                        await self.session.say(data[0]["answer"])
                        break
            except Exception as e:
                logger.error(f"[POLLING ERROR]: {e}")
                
            await asyncio.sleep(2)

    async def _send_help_request(self, text: str):
        try:
            logger.info(f"[HELP REQUEST] Sending to {BACKEND_URL}/help-request ...")
            resp = requests.post(
                f"{BACKEND_URL}/help-request",
                json={"customer_name": "Caller", "question": text},
                timeout=10,
            )
            logger.info(f"[HELP REQUEST SENT]: {resp.status_code} {resp.text}")
            return resp.json()
        except Exception as e:
            logger.info(f"[HELP REQUEST ERROR]: {e}")

async def entrypoint(ctx: JobContext):
    # Agent session setup
    session = AgentSession(
        llm=openai.LLM.with_ollama(
            model="llama3.2:latest",
            base_url="http://localhost:11434/v1",
        ),
        tts=None, # Free Piper TTS
        stt=None,
        vad=silero.VAD.load()          
    )
    # session = AgentSession()
    agent = FrontLoopAgent()
    await session.start(
        room = ctx.room,
        agent = agent
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))