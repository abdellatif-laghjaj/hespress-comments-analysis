from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Comment(BaseModel):
    user_name: str
    comment_text: str
    date: datetime
    likes: int
    article_url: str
    article_title: str
    batch_id: Optional[str] = None
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    sentiment: Optional[str] = None
