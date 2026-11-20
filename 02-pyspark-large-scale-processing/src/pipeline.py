"""Local PySpark ETL pipeline for synthetic catalogue data."""
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F


def transform_products(source: DataFrame) -> tuple[DataFrame, DataFrame]:
    typed = (
        source.withColumn("price_num", F.col("price").cast("double"))
        .withColumn("stock_num", F.col("stock").cast("integer"))
        .withColumn("rating_num", F.col("rating").cast("double"))
    )
    invalid = typed.filter(
        F.col("price_num").isNull()
        | (F.col("price_num") <= 0)
        | F.col("stock_num").isNull()
        | (F.col("stock_num") < 0)
        | F.col("rating_num").isNull()
        | (F.col("rating_num") < 1)
        | (F.col("rating_num") > 5)
    )
    valid = (
        typed.filter(
            F.col("price_num").isNotNull()
            & (F.col("price_num") > 0)
            & F.col("stock_num").isNotNull()
            & (F.col("stock_num") >= 0)
            & F.col("rating_num").between(1, 5)
        )
        .select(
            "product_id", "sector", "category",
            F.col("price_num").alias("price"),
            F.col("stock_num").alias("stock"),
            F.col("rating_num").alias("rating"),
        )
        .withColumn("inventory_value", F.round(F.col("price") * F.col("stock"), 2))
    )
    return valid, invalid


def run_pipeline(input_path: Path, output_dir: Path, spark: SparkSession) -> dict[str, int]:
    raw = spark.read.option("header", True).csv(str(input_path))
    valid, invalid = transform_products(raw)
    sector_summary = (
        valid.groupBy("sector")
        .agg(
            F.count("*").alias("product_count"),
            F.round(F.sum("inventory_value"), 2).alias("total_inventory_value"),
            F.round(F.avg("price"), 2).alias("average_price"),
        )
    )
    category_summary = (
        valid.groupBy("category")
        .agg(
            F.count("*").alias("product_count"),
            F.round(F.avg("price"), 2).alias("average_price"),
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    valid.write.mode("overwrite").parquet(str(output_dir / "curated_products"))
    invalid.write.mode("overwrite").parquet(str(output_dir / "rejected_records"))
    sector_summary.write.mode("overwrite").parquet(str(output_dir / "sector_summary"))
    category_summary.write.mode("overwrite").parquet(str(output_dir / "category_summary"))
    return {"input": raw.count(), "accepted": valid.count(), "rejected": invalid.count()}


def main() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    input_path = project_dir / "data/raw/products.csv"
    if not input_path.exists():
        raise FileNotFoundError("Run python src/generate_data.py before the pipeline.")
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("synthetic-catalogue-processing")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        counts = run_pipeline(input_path, project_dir / "data/processed", spark)
        print(f"Pipeline complete: {counts}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
