import json
import os
import re
import pymupdf as fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import POLICY_DIR, INDEX_DIR, EMBEDDING_MODEL

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

def chunk_text(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks

def main():
    os.makedirs(POLICY_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    pdfs = sorted(n for n in os.listdir(POLICY_DIR) if n.lower().endswith(".pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {POLICY_DIR}. Add approved HR policy PDFs first.")
    records = []
    for filename in pdfs:
        with fitz.open(os.path.join(POLICY_DIR, filename)) as pdf:
            for page_no, page in enumerate(pdf, start=1):
                for chunk in chunk_text(page.get_text()):
                    records.append({"text": chunk, "source": f"{filename}, page {page_no}"})
    if not records:
        raise SystemExit("No extractable text found. Scanned PDFs may need OCR.")
    model = SentenceTransformer(EMBEDDING_MODEL)
    vectors = model.encode([r["text"] for r in records], normalize_embeddings=True, show_progress_bar=True)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, os.path.join(INDEX_DIR, "policies.faiss"))
    with open(os.path.join(INDEX_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Indexed {len(records)} chunks from {len(pdfs)} PDF(s).")

if __name__ == "__main__":
    main()
