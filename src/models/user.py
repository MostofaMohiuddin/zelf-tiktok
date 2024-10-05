from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    tiktok_unique_id: str
    sec_uid: str
    follower_count: int
    following_count: int
    video_count: int
    like_count: int
    id: Optional[int] = None
