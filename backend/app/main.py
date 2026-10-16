from collections import defaultdict, deque
from threading import Lock
from time import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_ORIGIN, RATE_LIMIT_PER_MINUTE
from app.schemas import ChatRequest, ChatResponse
from app.guardrails.input_guardrail import validate_input
from app.guardrails.retrieval_guardrail import retrieve_relevant_policies
from app.guardrails.output_guardrail import validate_output
from app.services.gemini_service import generate_policy_answer

app = FastAPI(title="HR Policy Chatbot API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Demo-only in-memory rate limiter; use Redis/shared storage for multiple workers.
_requests = defaultdict(deque)
_lock = Lock()

@app.get("/health")
def health():
    return {"status": "ok"}

def enforce_rate_limit(request: Request):
    now = time()
    ip = request.client.host if request.client else "unknown"
    with _lock:
        bucket = _requests[ip]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MINUTE:
            raise HTTPException(429, "Too many requests. Please try again shortly.")
        bucket.append(now)



import logging

logger = logging.getLogger(__name__)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    enforce_rate_limit(request)
    question = validate_input(payload.question)  # Tier 1
    try:
        docs = retrieve_relevant_policies(question)  # Tier 2
    except Exception:
        raise HTTPException(503, "Policy search is temporarily unavailable.")
    if not docs:
        return ChatResponse(answer="I couldn't find a relevant answer in the available HR policy documents. Please contact HR for clarification.")
    passages = [{"text": d.text, "source": d.source} for d in docs]
    try:
        candidate = generate_policy_answer(question, passages)
        return validate_output(candidate, {p["source"] for p in passages})  # Tier 3
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc
