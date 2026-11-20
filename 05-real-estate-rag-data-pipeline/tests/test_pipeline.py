import csv
import json

from src.pipeline import run_pipeline, property_document
from src.search import search_documents


def test_pipeline_accepts_valid_and_rejects_invalid_rows(tmp_path):
    source = tmp_path / "properties.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["property_id", "title", "description", "city", "property_type", "price", "area_sqft", "bedrooms"])
        writer.writerow(["A1", "Family flat", "Near a school", "kolkata", "apartment", "5000000", "1000", "2"])
        writer.writerow(["A2", "Broken flat", "Bad price", "Pune", "apartment", "N/A", "800", "2"])
    output = tmp_path / "out"
    assert run_pipeline(source, output) == {"accepted": 1, "rejected": 1}
    documents = [json.loads(line) for line in (output / "property_documents.jsonl").read_text().splitlines()]
    assert documents[0]["metadata"]["city"] == "Kolkata"
    assert "Family flat" in documents[0]["text"]


def test_duplicate_property_ids_are_rejected(tmp_path):
    source = tmp_path / "properties.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["property_id", "title", "description", "city", "property_type", "price", "area_sqft", "bedrooms"])
        writer.writerow(["DUP", "One", "Desc", "Kolkata", "Flat", "100", "10", "1"])
        writer.writerow(["DUP", "Two", "Desc", "Kolkata", "Flat", "200", "20", "2"])
    assert run_pipeline(source, tmp_path / "out") == {"accepted": 1, "rejected": 1}


def test_keyword_retrieval_ranks_matching_documents():
    docs = [
        {"property_id": "P2", "text": "Studio apartment near office"},
        {"property_id": "P1", "text": "Family home near school and park"},
    ]
    results = search_documents("family home school", docs)
    assert results[0]["property_id"] == "P1"


def test_property_document_contains_searchable_attributes():
    record = {
        "property_id": "P1", "title": "Modern flat", "description": "Near metro",
        "city": "Kolkata", "property_type": "Apartment", "price": 100,
        "area_sqft": 900, "bedrooms": 2,
    }
    document = property_document(record)
    assert document["metadata"]["bedrooms"] == 2
    assert "900 square feet" in document["text"]
