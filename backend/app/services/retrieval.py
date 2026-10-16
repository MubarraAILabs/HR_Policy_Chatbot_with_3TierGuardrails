import json
import os
from functools import lru_cache
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, INDEX_DIR

class PolicyRetriever:
    def __init__(self):
        index_path = os.path.join(INDEX_DIR, "policies.faiss")
        metadata_path = os.path.join(INDEX_DIR, "metadata.json")
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("FAISS index missing. Add PDFs and run python -m app.ingestion")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = faiss.read_index(index_path)
        with open(metadata_path, encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        vector = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(np.asarray(vector, dtype="float32"), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.metadata):
                item = self.metadata[idx]
                results.append({"text": item["text"], "source": item["source"], "score": float(score)})
        return results

@lru_cache(maxsize=1)
def get_retriever():
    try:
        return PolicyRetriever()
    except FileNotFoundError:
        return None
