from typing import List
import uuid
from datetime import datetime
import logging
import pandas as pd
from storage.mongodb_handler import MongoDBHandler
from storage.kafka_handler import KafkaHandler
from utils.scrapper import HespressCommentsScraper
from storage.hdfs_handler import HDFSHandler
from models.comment import Comment
from utils.sentiments_processor import SentimentProcessor


class BatchProcessor:
    def __init__(
            self,
            mongodb_handler: MongoDBHandler,
            kafka_handler: KafkaHandler,
            hdfs_handler: HDFSHandler,
            sentiment_processor: SentimentProcessor = None
    ):
        self.mongodb_handler = mongodb_handler
        self.hdfs_handler = hdfs_handler
        self.kafka_handler = kafka_handler
        self.scraper = HespressCommentsScraper()
        self.sentiment_processor = sentiment_processor or SentimentProcessor(
            model_path="model/sentiment_model.h5",
            tokenizer_path="model/tokenizer.json",
            label_encoder_path="model/label_encoder.pkl"
        )
        self.logger = logging.getLogger(__name__)

    def process_urls(self, urls: List[str]):
        batch_id = str(uuid.uuid4())
        self.logger.info(f"Starting batch processing with ID: {batch_id}")

        try:
            # Get existing comment IDs before scraping
            existing_comment_ids = self.mongodb_handler.get_existing_comment_ids()

            df = self.scraper.fetch_comments(urls, existing_comment_ids)

            if df.empty:  # Check if the DataFrame is empty
                self.logger.info("No new comments found.")
                return None  # Or handle it differently as needed

            # Predict sentiments (only if df is not empty)
            sentiments = self.sentiment_processor.predict(
                df['Comment'].tolist()
            )

            # Convert numerical sentiments to string labels
            sentiment_mapping = {-1: "negative", 0: "neutral", 1: "positive"}  # Define your mapping
            string_sentiments = [sentiment_mapping.get(s, "unknown") for s in sentiments]  # Handle unknown values

            # Add sentiment column
            df['Sentiment'] = string_sentiments

            # Convert to Comment models and prepare for Kafka
            comments = []
            kafka_messages = []
            for _, row in df.iterrows():
                comment = Comment(
                    user_name=row['User Name'],
                    comment_text=row['Comment'],
                    date=row['Date'].isoformat() if pd.notna(row['Date']) else None,  # Convert to ISO string
                    likes=row['Likes'],
                    article_url=row['Article URL'],
                    article_title=row['Article Title'],
                    sentiment=row['Sentiment'],
                    batch_id=batch_id,
                    comment_id=row['comment_id'],
                )
                comments.append(comment)
                kafka_messages.append(comment.dict())

            hdfs_path = f"/hespress_comments/batch_{batch_id}.json"
            self.hdfs_handler.save_to_hdfs(kafka_messages, hdfs_path)

            # Read back from HDFS
            comments_from_hdfs = self.hdfs_handler.read_from_hdfs(hdfs_path)
            self.mongodb_handler.save_batch([Comment(**c) for c in comments_from_hdfs], batch_id)

            # Send to Kafka
            self.kafka_handler.send_comments(kafka_messages)

            # Update merged view
            self.mongodb_handler.update_merged_view()

            self.logger.info(f"Batch processing completed for batch {batch_id}")
            return batch_id

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise
