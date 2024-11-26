from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from storage.mongodb_handler import MongoDBHandler
from config.mongodb_config import MongoDBConfig
import logging


class SparkKafkaProcessor:
    def __init__(self, mongodb_config: MongoDBConfig):
        self.logger = logging.getLogger(__name__)
        self.mongodb_config = mongodb_config

        # Initialize Spark Session
        self.spark = SparkSession.builder \
            .appName("HespressCommentsProcessor") \
            .config("spark.mongodb.output.uri",
                    f"mongodb://{mongodb_config.host}:{mongodb_config.port}/{mongodb_config.database}.{mongodb_config.realtime_collection}") \
            .config("spark.jars.packages",
                    "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
            .getOrCreate()

        # Define comment schema
        self.comment_schema = StructType([
            StructField("user_name", StringType(), True),
            StructField("comment_text", StringType(), True),
            StructField("date", TimestampType(), True),
            StructField("likes", IntegerType(), True),
            StructField("article_url", StringType(), True),
            StructField("article_title", StringType(), True),
            StructField("batch_id", StringType(), True),
            StructField("processing_timestamp", TimestampType(), True)
        ])

    def process_kafka_stream(self, kafka_bootstrap_servers: str, topic: str):
        """
        Process Kafka stream and write to MongoDB
        """
        try:
            # Read from Kafka
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
                .option("subscribe", topic) \
                .load()

            # Parse the value
            parsed_df = df.select(
                from_json(col("value").cast("string"), self.comment_schema).alias("comment")
            ).select("comment.*")

            # Write to MongoDB using streaming
            query = parsed_df \
                .writeStream \
                .format("mongodb") \
                .option("checkpointLocation", "/tmp/checkpoint") \
                .option("forceInsert", "true") \
                .start()

            # Await termination
            query.awaitTermination()

        except Exception as e:
            self.logger.error(f"Error processing Kafka stream: {str(e)}")
        finally:
            self.spark.stop()
