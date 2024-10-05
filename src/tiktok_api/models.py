from typing import List, Optional
from pydantic import BaseModel


class TikTokVideoListResponse(BaseModel):
    videos: List[dict]
    cursor: str
    has_more: bool
    search_id: Optional[str] = None


class TikTokCommentListResponse(BaseModel):
    comments: List[dict]
    cursor: str
    has_more: bool
