from pyspark.sql import SparkSession

from src.pipeline import transform_products


def test_transform_separates_invalid_records(spark):
    rows = [
        ("A", "Grocery", "Essentials", "10.5", "4", "4.2"),
        ("B", "Fashion", "Apparel", "invalid", "3", "3.8"),
        ("C", "Home", "Decor", "20", "-1", "4.0"),
    ]
    columns = ["product_id", "sector", "category", "price", "stock", "rating"]
    source = spark.createDataFrame(rows, columns)

    valid, rejected = transform_products(source)

    assert valid.count() == 1
    assert rejected.count() == 2
    record = valid.first()
    assert record["product_id"] == "A"
    assert record["inventory_value"] == 42.0


def test_transform_keeps_zero_stock_as_valid(spark):
    rows = [("A", "Grocery", "Essentials", "10", "0", "4.0")]
    columns = ["product_id", "sector", "category", "price", "stock", "rating"]
    source = spark.createDataFrame(rows, columns)

    valid, rejected = transform_products(source)

    assert valid.count() == 1
    assert rejected.count() == 0
    assert valid.first()["inventory_value"] == 0.0


# A session-scoped local Spark fixture keeps the test setup reproducible.
import pytest


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder.master("local[1]")
        .appName("portfolio-pyspark-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
