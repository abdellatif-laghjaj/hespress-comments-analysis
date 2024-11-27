import json
from typing import List, Dict
import logging
from hdfs import InsecureClient


class HDFSHandler:
    def __init__(self, host: str, port: int):
        self.client = InsecureClient(f"http://{host}:{port}")
        self.logger = logging.getLogger(__name__)

    def save_to_hdfs(self, data: List[Dict], hdfs_path: str):
        """Saves data to HDFS."""
        try:
            with self.client.write(hdfs_path, encoding='utf-8') as writer:
                json.dump(data, writer, ensure_ascii=False)
            self.logger.info(f"Successfully saved data to HDFS: {hdfs_path}")
        except Exception as e:
            self.logger.error(f"Error saving data to HDFS: {str(e)}")
            raise

    def read_from_hdfs(self, hdfs_path: str) -> List[Dict]:
        """Reads data from HDFS."""
        try:
            with self.client.read(hdfs_path, encoding='utf-8') as reader:
                data = json.load(reader)
            self.logger.info(f"Successfully read data from HDFS: {hdfs_path}")
            return data
        except Exception as e:
            self.logger.error(f"Error reading data from HDFS: {str(e)}")
            raise
