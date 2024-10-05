from typing import Optional
from pydantic import BaseModel


class Keyword(BaseModel):
    text: str
    search_id: str
    last_fetched_cursor: str
    has_more: bool
    id: Optional[int] = None
