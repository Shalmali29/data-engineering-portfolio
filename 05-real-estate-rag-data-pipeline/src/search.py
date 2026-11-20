"""Simple local keyword retrieval over prepared property documents."""
import json
import re
import sys
from pathlib import Path


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def search_documents(query: str, documents: list[dict], limit: int = 5) -> list[dict]:
    query_terms = tokenize(query)
    scored = []
    for document in documents:
        document_terms = tokenize(document["text"])
        overlap = len(query_terms & document_terms)
        if overlap:
            scored.append((overlap / max(len(query_terms), 1), document))
    scored.sort(key=lambda item: (-item[0], item[1]["property_id"]))
    return [{"score": round(score, 4), **doc} for score, doc in scored[:limit]]


def load_documents(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main():
    project = Path(__file__).resolve().parents[1]
    docs_path = project / "data/processed/property_documents.jsonl"
    if not docs_path.exists():
        from .pipeline import run_pipeline
        run_pipeline(project / "data/raw/properties.csv", project / "data/processed")
    query = " ".join(sys.argv[1:]) or "apartment"
    for result in search_documents(query, load_documents(docs_path)):
        print(f"{result['score']:.2f} | {result['property_id']} | {result['text']}")


if __name__ == "__main__":
    main()
