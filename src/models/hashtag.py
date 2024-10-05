from typing import Optional
from pydantic import BaseModel
from src.models.video import Video


class Hashtag(BaseModel):
    text: str
    challenge_id: int
    last_fetched_cursor: str
    has_more: bool
    view_count: int
    video_count: int
    id: Optional[int] = None


# class HashtagVideosResponse(BaseModel):
#     videos: list[Video]
#     has_more: bool
#     cursor: str
