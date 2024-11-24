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


if __name__ == "__main__":
    main()
