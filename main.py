import logging
import schedule
import time
import traceback
import requests
from storage.hdfs_handler import HDFSHandler
from config.mongodb_config import MongoDBConfig
from config.kafka_config import KafkaConfig
from storage.mongodb_handler import MongoDBHandler
from storage.kafka_handler import KafkaHandler
from processors.batch_processor import BatchProcessor
import six
import sys
from utils.sentiments_processor import SentimentProcessor
from datetime import datetime

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


def scheduled_batch_process(batch_processor, urls):
    try:
        logger.info(f"Starting scheduled batch processing at {datetime.now()}")
        batch_id = batch_processor.process_urls(urls)
        logger.info(f"Finished scheduled batch processing for batch {batch_id} at {datetime.now()}")
    except Exception as e:
        logger.error(f"Error during scheduled batch processing: {str(e)}")
        logger.error(traceback.format_exc())  # Include traceback for detailed error info


def main():
    try:
        logger.info("Starting main application")

        # Initialize configurations
        mongodb_config = MongoDBConfig()
        kafka_config = KafkaConfig()
        hdfs_handler = HDFSHandler(host="localhost", port=9870)

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
            mongodb_handler=mongodb_handler,
            hdfs_handler=hdfs_handler,
            kafka_handler=kafka_handler,
            sentiment_processor=sentiment_processor
        )

        # Example URLs to process
        urls = [
            "https://www.hespress.com/%d8%a7%d9%84%d9%85%d9%84%d9%83-%d9%8a%d8%b7%d8%a7%d9%84%d8%a8-%d8%a8%d8%a7%d9%84%d8%aa%d8%ad%d8%b1%d9%83-%d8%a7%d9%84%d8%b9%d8%a7%d8%ac%d9%84-%d9%88%d8%a7%d9%84%d9%81%d9%88%d8%b1%d9%8a-%d9%84%d9%88-1471217.html",
        ]

        # Modify the scheduled processing to use the API endpoint
        def scheduled_batch_process_with_dynamic_url(batch_processor):
            # Get the current URL from the API endpoint
            response = requests.get('http://localhost:5000/api/url')
            current_url = response.json().get('url')

            if current_url:
                try:
                    logger.info(f"Processing URL: {current_url}")
                    batch_processor.process_urls([current_url])
                except Exception as e:
                    logger.error(f"Error processing URL {current_url}: {str(e)}")
            else:
                logger.info("No URL set for processing")

        # Schedule the batch processing job
        schedule.every().minute.do(scheduled_batch_process_with_dynamic_url, batch_processor)

        # Keep the application running and check for scheduled jobs
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except Exception as e:
        logger.error(f"Critical error in main process: {str(e)}")
        logger.error(traceback.format_exc())  # Include traceback for detailed error info


if __name__ == "__main__":
    main()
