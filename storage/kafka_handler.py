import json
from kafka import KafkaProducer, KafkaConsumer
from config.kafka_config import KafkaConfig
import logging
from typing import List, Dict


class KafkaHandler:
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Producer configuration
        self.producer = KafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Consumer configuration
        self.consumer = KafkaConsumer(
            self.config.comments_topic,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def send_comments(self, comments: List[Dict]):
        """
        Send comments to Kafka topic
        """
        try:
            for comment in comments:
                self.producer.send(
                    self.config.comments_topic,
                    value=comment
                )
            self.producer.flush()
            self.logger.info(f"Sent {len(comments)} comments to Kafka")
        except Exception as e:
            self.logger.error(f"Error sending comments to Kafka: {str(e)}")

    def consume_comments(self):
        """
        Consume comments from Kafka topic
        """
        try:
            for message in self.consumer:
                yield message.value
        except Exception as e:
            self.logger.error(f"Error consuming from Kafka: {str(e)}")
