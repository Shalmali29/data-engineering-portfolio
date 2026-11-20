from src.quality import process_batch, validate_record


def valid(product_id="P-1"):
    return {
        "product_id": product_id,
        "title": "Sample product",
        "category": "Home",
        "price": "10.50",
        "availability": "in_stock",
    }


def test_valid_record_passes():
    assert validate_record(valid()) == []


def test_invalid_price_and_availability_are_flagged():
    row = valid()
    row.update(price="NaN", availability="available")
    errors = validate_record(row)
    assert "invalid_price_range" in errors
    assert "invalid_availability" in errors


def test_duplicate_ids_are_quarantined():
    result = process_batch([valid(), valid()], warning_threshold=50, failure_threshold=20)
    assert result["accepted_records"] == 1
    assert result["quarantined"][0]["errors"] == ["duplicate_product_id"]


def test_quality_status_thresholds():
    rows = [valid("A"), valid("B"), valid("C"), valid("D"), valid("E")]
    bad = valid("F")
    bad["price"] = "bad"
    result = process_batch(rows + [bad], warning_threshold=95, failure_threshold=80)
    assert result["quality_score_percent"] == 83.33
    assert result["status"] == "WARNING"


def test_empty_batch_fails():
    assert process_batch([])["status"] == "FAILED"


def test_invalid_threshold_order_raises():
    try:
        process_batch([], warning_threshold=70, failure_threshold=80)
    except ValueError as exc:
        assert "Thresholds" in str(exc)
    else:
        raise AssertionError("Expected invalid thresholds to fail")
