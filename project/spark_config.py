"""
SparkSession factory and configuration helpers.

Usage
-----
    from spark_config import create_spark_session

    spark = create_spark_session()          # local mode, sensible defaults
    spark = create_spark_session("prod")    # cluster-optimised settings
"""

import logging
import os
from pyspark.sql import SparkSession


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default configuration profiles
# ---------------------------------------------------------------------------

_BASE_CONFIG = {
    # Serialisation
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    # SQL / Catalyst optimisations
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    # Parquet settings
    "spark.sql.parquet.compression.codec": "snappy",
    "spark.sql.parquet.filterPushdown": "true",
    "spark.sql.parquet.mergeSchema": "false",
    # Shuffle
    "spark.sql.shuffle.partitions": "200",
    # Broadcast join threshold (10 MB)
    "spark.sql.autoBroadcastJoinThreshold": str(10 * 1024 * 1024),
    # Timezone
    "spark.sql.session.timeZone": "UTC",
}

_LOCAL_OVERRIDES = {
    "spark.master": "local[*]",
    "spark.driver.memory": "2g",
    "spark.sql.shuffle.partitions": "8",   # keep it small for local runs
}

_PROD_OVERRIDES = {
    "spark.driver.memory": "8g",
    "spark.executor.memory": "16g",
    "spark.executor.cores": "4",
    "spark.sql.shuffle.partitions": "400",
}

PROFILES = {
    "local": {**_BASE_CONFIG, **_LOCAL_OVERRIDES},
    "prod": {**_BASE_CONFIG, **_PROD_OVERRIDES},
}


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def create_spark_session(
    profile: str = "local",
    app_name: str = "ChicagoETL",
    extra_config: dict | None = None,
    enable_delta: bool = False,
) -> SparkSession:
    """Create and return a configured :class:`~pyspark.sql.SparkSession`.

    Parameters
    ----------
    profile:
        Configuration profile to use – ``"local"`` (default) or ``"prod"``.
    app_name:
        Spark application name shown in the Spark UI.
    extra_config:
        Optional dict of additional Spark configuration key/value pairs that
        override the profile settings.
    enable_delta:
        When ``True``, adds the Delta Lake extension and its SQL parser so that
        Delta tables can be read/written.  Requires ``delta-spark`` to be
        installed and the matching Delta JAR to be present on the classpath.

    Returns
    -------
    SparkSession
    """
    config = dict(PROFILES.get(profile, PROFILES["local"]))
    if extra_config:
        config.update(extra_config)

    builder = SparkSession.builder.appName(app_name)

    if enable_delta:
        config["spark.sql.extensions"] = (
            "io.delta.sql.DeltaSparkSessionExtension"
        )
        config["spark.sql.catalog.spark_catalog"] = (
            "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )

    for key, value in config.items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()
    _configure_logging(spark)
    logger.info("SparkSession created (profile=%s, app=%s)", profile, app_name)
    return spark


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def _configure_logging(spark: SparkSession) -> None:
    """Quieten verbose Spark / log4j output and set up Python logging."""
    sc = spark.sparkContext
    sc.setLogLevel("WARN")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
