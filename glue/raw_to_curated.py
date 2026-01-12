import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

from pyspark.sql.functions import (
    col,
    from_unixtime,
    input_file_name,
    regexp_extract,
    lit,
    row_number,
    current_date,
    date_sub
)
from pyspark.sql.window import Window


# Glue boilerplate

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


# S3 Paths

RAW_PATH = "s3://earthquake-dev-prathyusha-data/earthquake/raw/"
CURATED_V2_PATH = (
    "s3://earthquake-dev-prathyusha-data/"
    "earthquake/curated/earthquakes_history_v2/"
)


#  Read RAW data (IMMUTABLE)

raw_df = (
    spark.read
    .option("mergeSchema", "true")
    .json(RAW_PATH)
)


#  Extract dt/hour from S3 path

raw_df = raw_df.withColumn("_file", input_file_name())

raw_df = raw_df.withColumn(
    "dt",
    regexp_extract(col("_file"), r"/dt=([0-9]{4}-[0-9]{2}-[0-9]{2})/", 1)
)

raw_df = raw_df.withColumn(
    "hour",
    regexp_extract(col("_file"), r"/hour=([0-9]{1,2})/", 1)
)

raw_df = raw_df.filter((col("dt") != "") & (col("hour") != ""))


#  INCREMENTAL FIX
#     Process only last 48 hours of RAW

raw_df = raw_df.filter(
    col("dt") >= date_sub(current_date(), 2)
)


#  Flatten schema

flat = raw_df.select(
    col("feature.id").alias("quake_id"),
    col("feature.properties.mag").cast("double").alias("mag"),
    col("feature.properties.place").alias("place"),
    col("feature.properties.title").alias("title"),
    col("feature.properties.time").cast("long").alias("event_time_ms"),
    col("feature.properties.updated").cast("long").alias("updated_ms"),
    col("feature.geometry.coordinates")[0].cast("double").alias("lon"),
    col("feature.geometry.coordinates")[1].cast("double").alias("lat"),
    col("feature.geometry.coordinates")[2].cast("double").alias("depth_km"),
    col("dt"),
    col("hour")
)


#  Data quality rules

flat = flat.filter(col("quake_id").isNotNull() & (col("quake_id") != ""))
flat = flat.filter(col("mag") >= 0)
flat = flat.filter((col("lat") >= -90) & (col("lat") <= 90))
flat = flat.filter((col("lon") >= -180) & (col("lon") <= 180))


#  Deduplication
#    (quake_id + updated_ms)

w = Window.partitionBy("quake_id", "updated_ms").orderBy(col("updated_ms").desc())

deduped = (
    flat
    .withColumn("rn", row_number().over(w))
    .filter(col("rn") == 1)
    .drop("rn")
)


#  Enrichment

final_df = (
    deduped
    .withColumn("event_time", from_unixtime(col("event_time_ms") / 1000))
    .withColumn("updated_time", from_unixtime(col("updated_ms") / 1000))
    .withColumn("pipeline_type", lit("batch"))
)


#  Write curated history (append-only)

(
    final_df.write
    .mode("append")
    .partitionBy("dt", "hour")
    .parquet(CURATED_V2_PATH)
)

job.commit()