from pymongo import MongoClient
from config.mongodb_config import MongoDBConfig
from models.comment import Comment
from typing import List
import logging


class MongoDBHandler:
    def __init__(self, config: MongoDBConfig):
        self.config = config
        self.client = MongoClient(config.host, config.port)
        self.db = self.client[config.database]
        self.logger = logging.getLogger(__name__)

    def save_batch(self, comments: List[Comment], batch_id: str):
        try:
            comments_dict = [comment.dict() for comment in comments]
            for comment in comments_dict:
                comment['batch_id'] = batch_id

            # Ensure sentiment is saved (even if it's None)
            self.db[self.config.batch_collection].insert_many(comments_dict)
            self.logger.info(f"Saved {len(comments)} comments in batch {batch_id}")
        except Exception as e:
            self.logger.error(f"Error saving batch: {str(e)}")
            raise

    def update_merged_view(self):
        # Same as before, but now includes sentiment in the merge
        pipeline = [
            {
                '$unionWith': {
                    'coll': self.config.realtime_collection
                }
            },
            {
                '$group': {
                    '_id': {
                        'article_url': '$article_url',
                        'user_name': '$user_name',
                        'comment_text': '$comment_text'
                    },
                    'latest_record': {'$last': '$$ROOT'}
                }
            },
            {
                '$replaceRoot': {'newRoot': '$latest_record'}
            }
        ]

        try:
            self.db[self.config.merged_collection].drop()
            result = self.db[self.config.batch_collection].aggregate(pipeline)
            self.db[self.config.merged_collection].insert_many(list(result))
            self.logger.info("Updated merged view successfully")
        except Exception as e:
            self.logger.error(f"Error updating merged view: {str(e)}")
            raise
