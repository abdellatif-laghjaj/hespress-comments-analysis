from dataclasses import dataclass

@dataclass
class KafkaConfig:
    bootstrap_servers: str = "localhost:9092"
    topic: str = "hespress_comments"
    group_id: str = "comments_processor"