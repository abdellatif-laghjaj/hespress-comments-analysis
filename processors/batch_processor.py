from typing import List
import uuid
from datetime import datetime
import logging
from storage.mongodb_handler import MongoDBHandler
from storage.kafka_handler import KafkaHandler
from models.comment import Comment
from config.kafka_config import KafkaConfig
from utils.scrapper import HespressCommentsScraper


class BatchProcessor:
    def __init__(self,
                 mongodb_handler: MongoDBHandler,
                 kafka_handler: KafkaHandler):
        self.mongodb_handler = mongodb_handler
        self.kafka_handler = kafka_handler
        self.scraper = HespressCommentsScraper()
        self.logger = logging.getLogger(__name__)

    def process_urls(self, urls: List[str]):
        batch_id = str(uuid.uuid4())
        self.logger.info(f"Starting batch processing with ID: {batch_id}")

        try:
            # Fetch comments using existing scraper
            df = self.scraper.fetch_comments(urls, save_to_csv=False)

            # Convert to Comment models and prepare for Kafka
            comments = []
            kafka_messages = []
            for _, row in df.iterrows():
                comment = Comment(
                    user_name=row['User Name'],
                    comment_text=row['Comment'],
                    date=row['Date'],
                    likes=row['Likes'],
                    article_url=row['Article URL'],
                    article_title=row['Article Title'],
                    batch_id=batch_id
                )
                comments.append(comment)

                # Prepare Kafka message
                kafka_messages.append(comment.dict())

            # Save to MongoDB
            self.mongodb_handler.save_batch(comments, batch_id)

            # Send to Kafka
            self.kafka_handler.send_comments(kafka_messages)

            # Update merged view
            self.mongodb_handler.update_merged_view()

            self.logger.info(f"Batch processing completed for batch {batch_id}")
            return batch_id

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise
