from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Comment(BaseModel):
    comment_id: str
    user_name: str
    comment_text: str
    date: str
    likes: int
    article_url: str
    article_title: str
    sentiment: Optional[str] = 'NEUTRAL'
    batch_id: Optional[str] = None
    processing_timestamp: str = datetime.now().isoformat()
