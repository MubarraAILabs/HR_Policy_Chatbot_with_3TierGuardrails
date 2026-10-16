from dataclasses import dataclass
from app.config import SIMILARITY_THRESHOLD
from app.services.retrieval import get_retriever

@dataclass
class RetrievedPolicy:
    text: str
    source: str
    score: float

def retrieve_relevant_policies(question: str) -> list[RetrievedPolicy]:
    retriever = get_retriever()
    if retriever is None:
        return []
    hits = retriever.search(question, top_k=5)
    return [
        RetrievedPolicy(text=h["text"], source=h["source"], score=h["score"])
        for h in hits if h["score"] >= SIMILARITY_THRESHOLD
    ]
