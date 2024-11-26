from dataclasses import dataclass, field
from typing import List


@dataclass
class KafkaConfig:
    bootstrap_servers: List[str] = field(default_factory=lambda: ['localhost:9092'])
    comments_topic: str = 'hespress_comments'
    group_id: str = 'hespress_comments_group'