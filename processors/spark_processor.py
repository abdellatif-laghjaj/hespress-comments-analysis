from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
import logging
import traceback
from utils.sentiments_processor import SentimentProcessor


class SparkKafkaProcessor:
    def __init__(self, mongodb_config):
        self.logger = logging.getLogger(__name__)
        self.mongodb_config = mongodb_config
        self.sentiment_processor = SentimentProcessor()

        try:
            # Initialize Spark Session with detailed configuration
            self.spark = SparkSession.builder \
                .appName("HespressCommentsProcessor") \
                .config("spark.master", "local[*]") \
                .config("spark.mongodb.output.uri",
                        f"mongodb://{mongodb_config.host}:{mongodb_config.port}/{mongodb_config.database}.{mongodb_config.realtime_collection}") \
                .config("spark.jars.packages",
                        "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
                .getOrCreate()

            # Define UDF for sentiment prediction
            @udf(returnType=StringType())
            def predict_sentiment(comment):
                return self.sentiment_processor.predict(comment)

            self.predict_sentiment = predict_sentiment

            self.logger.info("Spark Session initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing Spark Session: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def process_kafka_stream(self, kafka_bootstrap_servers: str, topic: str):
        try:
            self.logger.info(f"Starting Kafka stream processing for topic: {topic}")

            # Read from Kafka
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
                .option("subscribe", topic) \
                .load()

            # Process and add sentiment
            processed_df = df \
                .withColumn("sentiment", self.predict_sentiment(col("value"))) \
                .select("*")  # Modify as needed

            # Write to MongoDB
            query = processed_df \
                .writeStream \
                .outputMode("append") \
                .format("mongodb") \
                .option("checkpointLocation", "/tmp/checkpoint") \
                .option("spark.mongodb.output.uri",
                        f"mongodb://{self.mongodb_config.host}:{self.mongodb_config.port}/{self.mongodb_config.database}.{self.mongodb_config.realtime_collection}") \
                .start()

            self.logger.info("Kafka stream processing started")
            query.awaitTermination()

        except Exception as e:
            self.logger.error(f"Error processing Kafka stream: {str(e)}")
            self.logger.error(traceback.format_exc())
