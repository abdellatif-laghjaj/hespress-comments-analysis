from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Comment(BaseModel):
    user_name: str
    comment_text: str
    date: datetime
    likes: int
    article_url: str
    article_title: str
    sentiment: Optional[str] = 'NEUTRAL'
    batch_id: Optional[str] = None
    processing_timestamp: datetime = datetime.now()
