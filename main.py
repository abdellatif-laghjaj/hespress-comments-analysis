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
import traceback

from utils.sentiments_processor import SentimentProcessor

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('application.log')
    ]
)
logger = logging.getLogger(__name__)

if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves


def main():
    try:
        logger.info("Starting main application")

        # Initialize configurations
        mongodb_config = MongoDBConfig()
        kafka_config = KafkaConfig()

        # Initialize sentiment processor
        sentiment_processor = SentimentProcessor(
            model_path="model/sentiment_model.h5",
            tokenizer_path="model/tokenizer.json",
            label_encoder_path="model/label_encoder.pkl"
        )

        # Initialize handlers
        mongodb_handler = MongoDBHandler(mongodb_config)
        kafka_handler = KafkaHandler(kafka_config)

        # Initialize processors
        batch_processor = BatchProcessor(
            mongodb_handler,
            kafka_handler,
            sentiment_processor
        )

        # Example URLs to process
        urls = [
            "https://www.hespress.com/%d8%b8%d9%87%d9%88%d8%b1-%d8%a8%d9%88%d8%b1%d9%8a%d8%b7%d8%a9-%d8%a5%d9%84%d9%89-%d8%ac%d8%a7%d9%86%d8%a8-%d8%b9%d8%b1%d8%a7%d9%82%d8%ac%d9%8a-%d9%8a%d8%b3%d8%a7%d8%a6%d9%84-%d8%ad%d9%82%d9%8a%d9%82-1471306.html",
        ]

        # Process batch
        batch_id = batch_processor.process_urls(urls)
        logger.info(f"Successfully processed batch {batch_id}")

    except Exception as e:
        logger.error(f"Critical error in main process: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
