from typing import Optional
from src.database.base_repository import BaseRepository
from src.models.keyword import Keyword


class KeywordRepository(BaseRepository):
    def get_keyword_by_text(self, text) -> Optional[Keyword]:
        query = "SELECT * FROM keyword WHERE text = ?"
        response = self.execute_query_one(query, (text,))
        if response:
            return Keyword(**response)

    # class Keyword(BaseModel):
    #     id: int
    #     text: str
    #     search_id: str
    #     last_fetched_cursor: str
    #     has_more: bool

    def insert_keyword(self, keyword: Keyword):
        query = "INSERT INTO keyword (text, search_id, last_fetched_cursor, has_more) VALUES (?, ?, ?, ?)"
        return self.execute_query(
            query,
            (
                keyword.text,
                keyword.search_id,
                keyword.last_fetched_cursor,
                keyword.has_more,
            ),
        )

    def update_keyword(self, keyword: Keyword):
        query = (
            "UPDATE keyword SET last_fetched_cursor = ?, has_more = ? WHERE text = ?"
        )
        return self.execute_query(
            query,
            (
                keyword.last_fetched_cursor,
                keyword.has_more,
                keyword.text,
            ),
        )
