from app.schemas import ModelAnswer, ChatResponse

FALLBACK = (
    "I couldn't verify the answer from the available HR policy documents. "
    "Please contact HR for clarification."
)

def validate_output(candidate: ModelAnswer, retrieved_sources: set[str]) -> ChatResponse:
    # Citation provenance and abstention checks do not prove semantic entailment.
    if candidate.abstain or not candidate.answer.strip() or not candidate.sources:
        return ChatResponse(answer=FALLBACK)
    citations = set(candidate.sources)
    if not citations.issubset(retrieved_sources):
        return ChatResponse(answer=FALLBACK)
    return ChatResponse(answer=candidate.answer.strip(), sources=sorted(citations))
