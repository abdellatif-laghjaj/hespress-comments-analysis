import logging
from config.mongodb_config import MongoDBConfig
from storage.mongodb_handler import MongoDBHandler
from processors.batch_processor import BatchProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Initialize configurations
    mongodb_config = MongoDBConfig()

    # Initialize handlers
    mongodb_handler = MongoDBHandler(mongodb_config)

    # Initialize processors
    batch_processor = BatchProcessor(mongodb_handler)

    # Example URLs to process
    urls = [
        "https://www.hespress.com/article1",
        "https://www.hespress.com/article2"
    ]

    try:
        # Process batch
        batch_id = batch_processor.process_urls(urls)
        logger.info(f"Successfully processed batch {batch_id}")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")


if __name__ == "__main__":
    main()
