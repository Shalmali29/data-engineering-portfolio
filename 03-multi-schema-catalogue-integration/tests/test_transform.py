import json
from pathlib import Path

from src.catalogue import to_canonical, map_schema_a, map_schema_b, map_schema_c
from src.pipeline import run


def sample():
    return {
        "product_id": "P-1", "title": "Test Product", "description": "A test",
        "category": "Home", "price": "10.50", "currency": "EUR",
        "image_urls": "https://example.test/a.jpg|https://example.test/b.jpg",
        "variants_json": '[{"sku":"P-1-A","size":"M"}]',
        "warehouses_json": '[{"warehouse_id":"WH-1","stock":4},{"warehouse_id":"WH-2","stock":3}]',
    }


def test_canonical_model_calculates_total_stock():
    product, issues = to_canonical(sample())
    assert product["total_stock"] == 7
    assert product["price"] == "10.50"
    assert not any("required field" in issue for issue in issues)


def test_missing_description_is_reported_not_fabricated():
    row = sample()
    row["description"] = ""
    product, issues = to_canonical(row)
    assert product["description"] is None
    assert "description: missing optional content" in issues


def test_invalid_warehouse_stock_makes_total_unknown():
    row = sample()
    row["warehouses_json"] = '[{"warehouse_id":"WH-1","stock":"unknown"}]'
    product, issues = to_canonical(row)
    assert product["total_stock"] is None
    assert any("invalid stock" in issue for issue in issues)


def test_three_schemas_have_distinct_shapes():
    product, _ = to_canonical(sample())
    a, b, c = map_schema_a(product), map_schema_b(product), map_schema_c(product)
    assert a["id"] == b["productId"] == c["item_id"] == "P-1"
    assert b["inventory"]["total"] == 7
    assert c["media"]["image_urls"][0].endswith("a.jpg")


def test_pipeline_writes_three_outputs_and_report(tmp_path):
    source = tmp_path / "products.csv"
    source.write_text(
        "product_id,title,description,category,price,currency,image_urls,variants_json,warehouses_json\n"
        'P-1,Test Product,A test,Home,10.50,EUR,https://example.test/a.jpg,"[]","[]",\n',
        encoding="utf-8",
    )
    result = run(source, tmp_path / "processed")
    assert result["records_processed"] == 1
    for filename in ("schema_a.jsonl", "schema_b.jsonl", "schema_c.jsonl", "validation_report.json"):
        assert (tmp_path / "processed" / filename).exists()
    report = json.loads((tmp_path / "processed/validation_report.json").read_text())
    assert isinstance(report, list)
