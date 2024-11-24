from dataclasses import dataclass


@dataclass
class MongoDBConfig:
    host: str = "localhost"
    port: int = 27017
    database: str = "hespress_comments"
    batch_collection: str = "comments_batch"
    realtime_collection: str = "comments_realtime"
    merged_collection: str = "comments_merged"
