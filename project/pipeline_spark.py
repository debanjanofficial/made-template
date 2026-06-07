"""
PySpark-based ETL pipeline for Chicago Crime and Weather data.

Mirrors the class structure of pipeline.py but uses PySpark DataFrames instead
of pandas, enabling distributed processing of large-scale datasets.

Usage
-----
    python project/pipeline_spark.py
"""

import logging
import os
import subprocess
import json

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

from data_models import (
    CRIME_RAW_SCHEMA,
    WEATHER_SCHEMA,
    CRIME_PARTITION_COLS,
    WEATHER_PARTITION_COLS,
    CRIME_BUCKET_COL,
    CRIME_NUM_BUCKETS,
)
from spark_config import create_spark_session


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

class HelperService:
    """Utility for loading pipeline configuration from JSON."""

    def load_json(self, path: str) -> dict:
        """Return the contents of a JSON file as a dictionary."""
        with open(path, "r") as fh:
            return json.load(fh)


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class DataExtractor:
    """Downloads datasets from Kaggle and reads them into Spark DataFrames."""

    def __init__(self, spark: SparkSession, source_info: dict) -> None:
        self.spark = spark
        self.source_info = source_info
        self.extracted_data: dict[str, DataFrame] = {}

    def extract(self) -> None:
        """Download CSV files from Kaggle and load them as Spark DataFrames."""
        data_dir = self.source_info["data_dir"]
        os.makedirs(data_dir, exist_ok=True)

        for dataset in self.source_info["datasets"]:
            logger.info("Downloading dataset: %s", dataset)
            subprocess.run(
                [
                    "kaggle",
                    "datasets",
                    "download",
                    "-d",
                    dataset,
                    "--unzip",
                    "-p",
                    data_dir,
                ],
                check=True,
            )

        crime_path = os.path.join(data_dir, "Crimes_-_2001_to_Present.csv")
        weather_path = os.path.join(data_dir, "Chicago_Weather.csv")

        logger.info("Reading crime data from %s", crime_path)
        self.extracted_data["crime_data"] = (
            self.spark.read
            .option("header", "true")
            .option("inferSchema", "false")
            .schema(CRIME_RAW_SCHEMA)
            .csv(crime_path)
        )

        logger.info("Reading weather data from %s", weather_path)
        self.extracted_data["weather_data"] = (
            self.spark.read
            .option("header", "true")
            .option("inferSchema", "false")
            .schema(WEATHER_SCHEMA)
            .csv(weather_path)
        )

        self._validate_schemas()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_schemas(self) -> None:
        """Log basic data-quality metrics after loading."""
        for name, df in self.extracted_data.items():
            count = df.count()
            null_counts = {
                col: df.filter(F.col(col).isNull()).count()
                for col in df.columns
            }
            logger.info(
                "Dataset '%s': %d rows | nulls per column: %s",
                name,
                count,
                null_counts,
            )


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------

class DataTransformer:
    """Cleans and filters Spark DataFrames produced by DataExtractor."""

    # Columns removed from crime data after transformation
    _CRIME_DROP_COLS = ["Year", "Updated On", "Latitude", "Longitude"]

    def __init__(self, extracted_data: dict[str, DataFrame]) -> None:
        self.extracted_data = extracted_data
        self.transformed_data: dict[str, DataFrame] = {}

    def transform(self) -> None:
        """Apply all transformations."""
        self._transform_crime()
        self._transform_weather()

    # ------------------------------------------------------------------

    def _transform_crime(self) -> None:
        crime_df = self.extracted_data.get("crime_data")
        if crime_df is None:
            logger.warning("No crime data found; skipping crime transformation.")
            return

        # Parse the Date column (already loaded as string via raw schema)
        crime_df = crime_df.withColumn(
            "Date",
            F.to_timestamp(F.col("Date"), "MM/dd/yyyy hh:mm:ss a"),
        )

        # Filter to 2021–2024
        crime_df = crime_df.filter(
            (F.year(F.col("Date")) >= 2021) & (F.year(F.col("Date")) <= 2024)
        )

        # Remove unwanted columns (ignore errors if column is missing)
        existing_drop = [c for c in self._CRIME_DROP_COLS if c in crime_df.columns]
        crime_df = crime_df.drop(*existing_drop)

        # Add partition helper columns
        crime_df = (
            crime_df
            .withColumn("year", F.year(F.col("Date")))
            .withColumn("month", F.month(F.col("Date")))
        )

        # Remove rows with a null Date (coerce produced nulls)
        crime_df = crime_df.filter(F.col("Date").isNotNull())

        # Cache for reuse in downstream steps (e.g. saving to multiple sinks)
        crime_df.cache()

        self.transformed_data["crime_data_filtered"] = crime_df
        logger.info(
            "Crime transformation complete: %d rows retained.", crime_df.count()
        )

    def _transform_weather(self) -> None:
        weather_df = self.extracted_data.get("weather_data")
        if weather_df is None:
            logger.warning("No weather data found; skipping weather transformation.")
            return

        # Impute missing tmax / tmin with column medians (approx)
        for col_name in ("tmax", "tmin"):
            median_val = weather_df.approxQuantile(col_name, [0.5], 0.001)[0]
            weather_df = weather_df.fillna({col_name: median_val})
            logger.info("Filled missing '%s' values with median %.2f.", col_name, median_val)

        # Add partition helper column
        weather_df = weather_df.withColumn("year", F.year(F.col("date")))

        weather_df.cache()

        self.transformed_data["weather_data"] = weather_df
        logger.info("Weather transformation complete.")


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

class DataLoader:
    """Persists transformed Spark DataFrames to multiple sinks."""

    def __init__(
        self,
        spark: SparkSession,
        transformed_data: dict[str, DataFrame],
        db_path: str,
        data_dir: str,
    ) -> None:
        self.spark = spark
        self.transformed_data = transformed_data
        self.db_path = db_path
        self.data_dir = data_dir

    # ------------------------------------------------------------------
    # Parquet (primary analytical sink)
    # ------------------------------------------------------------------

    def save_to_parquet(self, output_dir: str | None = None) -> None:
        """Write each dataset to a partitioned Parquet directory."""
        base = output_dir or os.path.join(self.data_dir, "parquet")

        crime_df = self.transformed_data.get("crime_data_filtered")
        if crime_df is not None:
            path = os.path.join(base, "crime_data_filtered")
            (
                crime_df.write
                .mode("overwrite")
                .partitionBy(*CRIME_PARTITION_COLS)
                .parquet(path)
            )
            logger.info("Crime data written to Parquet at %s", path)

        weather_df = self.transformed_data.get("weather_data")
        if weather_df is not None:
            path = os.path.join(base, "weather_data")
            (
                weather_df.write
                .mode("overwrite")
                .partitionBy(*WEATHER_PARTITION_COLS)
                .parquet(path)
            )
            logger.info("Weather data written to Parquet at %s", path)

    # ------------------------------------------------------------------
    # CSV (interoperability / backward compatibility)
    # ------------------------------------------------------------------

    def save_to_csv(self, output_dir: str | None = None) -> None:
        """Write each dataset to a single-partition CSV file."""
        base = output_dir or self.data_dir
        os.makedirs(base, exist_ok=True)

        for name, df in self.transformed_data.items():
            out_path = os.path.join(base, f"{name}.csv")
            # Coalesce to 1 so that a single CSV file is produced.
            (
                df.coalesce(1).write
                .mode("overwrite")
                .option("header", "true")
                .csv(out_path + "_spark_tmp")
            )
            # Move the part file to the expected location
            _merge_spark_csv(out_path + "_spark_tmp", out_path)
            logger.info("Dataset '%s' saved to CSV at %s", name, out_path)

    # ------------------------------------------------------------------
    # SQLite (backward-compatible sink via pandas bridge)
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load transformed data into a SQLite database.

        Converts each Spark DataFrame to pandas for the SQLite write so that
        the existing tests.sh assertions continue to pass.
        """
        import sqlite3

        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        try:
            conn = sqlite3.connect(self.db_path)
            logger.info("Connected to SQLite database at %s", self.db_path)

            for table_name, df in self.transformed_data.items():
                logger.info("Writing table '%s' to SQLite …", table_name)
                pandas_df = df.toPandas()
                pandas_df.to_sql(table_name, conn, if_exists="replace", index=False)
                logger.info("Table '%s' written (%d rows).", table_name, len(pandas_df))

            conn.close()
            logger.info("All tables written to SQLite successfully.")
        except Exception as exc:
            logger.error("Error writing to SQLite: %s", exc)
            raise


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

class DataPipeline:
    """Orchestrates the PySpark ETL workflow."""

    def __init__(
        self,
        spark: SparkSession,
        helper_service: HelperService,
        extractor: DataExtractor,
        transformer: DataTransformer,
        loader: DataLoader,
    ) -> None:
        self.spark = spark
        self.helper_service = helper_service
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def on_extract(self, source_info: dict) -> dict[str, DataFrame]:
        self.extractor.source_info = source_info
        self.extractor.extract()
        return self.extractor.extracted_data

    def on_transform(self, extracted_data: dict[str, DataFrame]) -> dict[str, DataFrame]:
        self.transformer.extracted_data = extracted_data
        self.transformer.transform()
        return self.transformer.transformed_data

    def on_load(self, transformed_data: dict[str, DataFrame]) -> None:
        self.loader.transformed_data = transformed_data
        self.loader.load()

    def run_pipeline(self) -> None:
        """Execute the full Extract → Transform → Load workflow."""
        json_path = "project/source_info.json"
        if not os.path.exists(json_path):
            logger.error("source_info.json not found at '%s'.", json_path)
            return

        source_info = self.helper_service.load_json(json_path)

        extracted_data = self.on_extract(source_info)
        transformed_data = self.on_transform(extracted_data)

        self.on_load(transformed_data)

        # Also persist analytical outputs
        self.loader.save_to_parquet()
        self.loader.save_to_csv()

        logger.info("PySpark ETL pipeline completed successfully.")


# ---------------------------------------------------------------------------
# CSV merge utility
# ---------------------------------------------------------------------------

def _merge_spark_csv(spark_output_dir: str, target_path: str) -> None:
    """Move the single part file written by Spark to *target_path*.

    Spark's CSV writer creates a directory with one ``part-*.csv`` file when
    ``coalesce(1)`` is used.  This helper consolidates that into the expected
    single-file path.
    """
    import shutil
    import glob as _glob

    parts = _glob.glob(os.path.join(spark_output_dir, "part-*.csv"))
    if parts:
        shutil.move(parts[0], target_path)
    shutil.rmtree(spark_output_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s – %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    spark = create_spark_session(profile="local", app_name="ChicagoETL")

    source_info = {
        "data_dir": "data",
        "datasets": [
            "abantikabose/chicago-weather-data",
            "abantikabose/chicago-crime-dataset-post-covid",
        ],
    }

    helper_service = HelperService()
    extractor = DataExtractor(spark, source_info)
    transformer = DataTransformer(extractor.extracted_data)
    loader = DataLoader(
        spark,
        transformer.transformed_data,
        db_path="data/processed_data.db",
        data_dir=source_info["data_dir"],
    )

    pipeline = DataPipeline(spark, helper_service, extractor, transformer, loader)
    pipeline.run_pipeline()

    spark.stop()
    print("PySpark ETL pipeline execution completed successfully.")
