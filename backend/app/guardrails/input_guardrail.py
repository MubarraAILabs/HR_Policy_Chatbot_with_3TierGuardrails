import re
from fastapi import HTTPException
from app.config import MAX_QUESTION_LENGTH

# Heuristics only; this is not a complete prompt-injection detector.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(the\s+)?previous\s+instructions",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"show\s+me\s+your\s+hidden\s+instructions",
    r"bypass\s+(the\s+)?(guardrails|safety|security)",
    r"act\s+as\s+(an?\s+)?unrestricted",
]

def validate_input(question: str) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise HTTPException(400, "Please enter a question.")
    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise HTTPException(413, f"Question must be at most {MAX_QUESTION_LENGTH} characters.")
    if any(re.search(p, cleaned, re.IGNORECASE) for p in INJECTION_PATTERNS):
        raise HTTPException(400, "I can help with HR policy questions, but can't follow requests to override safety instructions.")
    return cleaned
