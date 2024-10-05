from typing import Optional

from pydantic import BaseModel


class Video(BaseModel):
    tiktok_video_id: str
    author_username: str
    author_id: int
    like_count: int
    view_count: int
    video_url: str
    description: str
    id: Optional[int] = None
    hashtag_id: Optional[int] = None
    keyword_id: Optional[int] = None
