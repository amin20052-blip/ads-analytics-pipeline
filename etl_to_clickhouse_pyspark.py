from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import clickhouse_connect



spark = SparkSession.builder \
    .appName("OzonAdsETL") \
    .config("spark.jars", "/path/to/postgresql-42.x.x.jar") \
    .getOrCreate()


df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/project_ads_db") \
    .option("dbtable", "raw_ad_events") \
    .option("user", "postgres") \
    .option("password", "admin2005") \
    .load()


agg_df = df.groupBy("placement", "device_type").agg(
    F.count("event_id").alias("impressions"),
    F.sum(F.when(F.col("is_click") == True, 1).otherwise(0)).alias("clicks"),
    F.avg("page_load_time_ms").alias("avg_load_time")
).withColumn("ctr", (F.col("clicks") / F.col("impressions")) * 100)

agg_df.show()