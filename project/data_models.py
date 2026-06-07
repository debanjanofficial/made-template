"""
Data models (PySpark StructType schemas) for the Chicago Crime and Weather datasets.

Defines explicit schemas for type safety and query optimisation, along with
partitioning and bucketing recommendations for large-scale workloads.
"""

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    BooleanType,
    TimestampType,
    LongType,
)


# ---------------------------------------------------------------------------
# Crime data schema
# ---------------------------------------------------------------------------
# Source: Kaggle – abantikabose/chicago-crime-dataset-post-covid
# Columns that are dropped during transformation (Year, Updated On, Latitude,
# Longitude) are intentionally omitted from the *transformed* schema below.
# The *raw* schema includes all columns for safe ingestion.

CRIME_RAW_SCHEMA = StructType([
    StructField("ID", LongType(), nullable=True),
    StructField("Case Number", StringType(), nullable=True),
    StructField("Date", StringType(), nullable=True),        # parsed later
    StructField("Block", StringType(), nullable=True),
    StructField("IUCR", StringType(), nullable=True),
    StructField("Primary Type", StringType(), nullable=True),
    StructField("Description", StringType(), nullable=True),
    StructField("Location Description", StringType(), nullable=True),
    StructField("Arrest", BooleanType(), nullable=True),
    StructField("Domestic", BooleanType(), nullable=True),
    StructField("Beat", IntegerType(), nullable=True),
    StructField("District", IntegerType(), nullable=True),
    StructField("Ward", IntegerType(), nullable=True),
    StructField("Community Area", IntegerType(), nullable=True),
    StructField("FBI Code", StringType(), nullable=True),
    StructField("X Coordinate", DoubleType(), nullable=True),
    StructField("Y Coordinate", DoubleType(), nullable=True),
    StructField("Year", IntegerType(), nullable=True),
    StructField("Updated On", StringType(), nullable=True),
    StructField("Latitude", DoubleType(), nullable=True),
    StructField("Longitude", DoubleType(), nullable=True),
    StructField("Location", StringType(), nullable=True),
])

# Transformed / analytics-ready schema (subset, typed correctly).
CRIME_SCHEMA = StructType([
    StructField("ID", LongType(), nullable=True),
    StructField("Case Number", StringType(), nullable=True),
    StructField("Date", TimestampType(), nullable=False),
    StructField("Block", StringType(), nullable=True),
    StructField("IUCR", StringType(), nullable=True),
    StructField("Primary Type", StringType(), nullable=True),
    StructField("Description", StringType(), nullable=True),
    StructField("Location Description", StringType(), nullable=True),
    StructField("Arrest", BooleanType(), nullable=True),
    StructField("Domestic", BooleanType(), nullable=True),
    StructField("Beat", IntegerType(), nullable=True),
    StructField("District", IntegerType(), nullable=True),
    StructField("Ward", IntegerType(), nullable=True),
    StructField("Community Area", IntegerType(), nullable=True),
    StructField("FBI Code", StringType(), nullable=True),
    StructField("X Coordinate", DoubleType(), nullable=True),
    StructField("Y Coordinate", DoubleType(), nullable=True),
    StructField("Location", StringType(), nullable=True),
])


# ---------------------------------------------------------------------------
# Weather data schema
# ---------------------------------------------------------------------------
# Source: Kaggle – abantikabose/chicago-weather-data

WEATHER_SCHEMA = StructType([
    StructField("date", TimestampType(), nullable=False),
    StructField("tmax", DoubleType(), nullable=True),   # daily max temperature
    StructField("tmin", DoubleType(), nullable=True),   # daily min temperature
    StructField("prcp", DoubleType(), nullable=True),   # precipitation
    StructField("snow", DoubleType(), nullable=True),   # snowfall
    StructField("wspd", DoubleType(), nullable=True),   # wind speed
])


# ---------------------------------------------------------------------------
# Partitioning & bucketing strategy
# ---------------------------------------------------------------------------
#
# Crime data
#   • Partition by YEAR(Date) and MONTH(Date) for time-range queries.
#   • Bucket by District (32 buckets) for spatial joins with weather data.
#
# Weather data
#   • Partition by YEAR(date) for seasonal / annual analysis.
#   • Bucket by a synthetic location key if multi-station data is added.
#
# These constants are consumed by pipeline_spark.py when writing Parquet or
# Delta Lake outputs.

CRIME_PARTITION_COLS = ["year", "month"]   # derived columns added in transform
WEATHER_PARTITION_COLS = ["year"]          # derived column added in transform
CRIME_BUCKET_COL = "District"
CRIME_NUM_BUCKETS = 32
WEATHER_NUM_BUCKETS = 4
