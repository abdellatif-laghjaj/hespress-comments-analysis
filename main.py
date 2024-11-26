import logging
import threading
from config.mongodb_config import MongoDBConfig
from config.kafka_config import KafkaConfig
from storage.mongodb_handler import MongoDBHandler
from storage.kafka_handler import KafkaHandler
from processors.batch_processor import BatchProcessor
from processors.spark_processor import SparkKafkaProcessor
import six
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves


def start_spark_processor(mongodb_config):
    """
    Start Spark Kafka processor in a separate thread
    """
    spark_processor = SparkKafkaProcessor(mongodb_config)
    spark_processor.process_kafka_stream(
        kafka_bootstrap_servers='localhost:9092',
        topic='hespress_comments'
    )


def main():
    # Initialize configurations
    mongodb_config = MongoDBConfig()
    kafka_config = KafkaConfig()
    print("mongodb_config", mongodb_config)

    # Initialize handlers
    mongodb_handler = MongoDBHandler(mongodb_config)
    kafka_handler = KafkaHandler(kafka_config)

    # Start Spark Processor in a separate thread
    spark_thread = threading.Thread(
        target=start_spark_processor,
        args=(mongodb_config,)
    )
    spark_thread.start()

    # Initialize processors
    batch_processor = BatchProcessor(
        mongodb_handler,
        kafka_handler
    )

    # Example URLs to process
    urls = [
        "https://www.hespress.com/%d8%b5%d9%86%d8%b5%d8%a7%d9%84-%d9%8a%d9%81%d8%b6%d8%ad-%d8%a7%d9%84%d8%a8%d9%86%d9%8a%d8%a9-%d8%a7%d9%84%d8%b4%d9%85%d9%88%d9%84%d9%8a%d8%a9-%d9%84%d9%84%d9%86%d8%b8%d8%a7%d9%85-%d8%a7%d9%84%d8%b9-1469722.html",
        "https://www.hespress.com/%d8%aa%d8%af%d8%a8%d9%8a%d8%b1-%d8%a7%d9%84%d9%85%d8%a7%d8%a1-%d9%81%d9%8a-%d8%a7%d9%84%d9%85%d8%ba%d8%b1%d8%a8-1469649.html",
        "https://www.hespress.com/%d8%b0%d9%83%d8%b1%d9%89-%d8%a7%d8%ae%d8%aa%d8%b7%d8%a7%d9%81-%d8%a7%d9%84%d9%85%d9%87%d8%af%d9%8a-%d8%a8%d9%86%d8%a8%d8%b1%d9%83%d8%a9-%d8%aa%d8%b9%d9%8a%d8%af-%d9%85%d8%b3%d8%a7%d8%a1%d9%84%d8%a9-1455984.html",
        "https://www.hespress.com/%d8%a7%d8%ad%d8%aa%d8%ac%d8%a7%d8%ac-%d8%b9%d9%85%d8%a7%d9%84-%d8%a7%d9%84%d8%a5%d9%86%d8%b9%d8%a7%d8%b4-%d8%a3%d9%85%d8%a7%d9%85-%d8%a7%d9%84%d8%a8%d8%b1%d9%84%d9%85%d8%a7%d9%86-1469534.html",
    ]

    try:
        # Process batch
        batch_id = batch_processor.process_urls(urls)
        logger.info(f"Successfully processed batch {batch_id}")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
