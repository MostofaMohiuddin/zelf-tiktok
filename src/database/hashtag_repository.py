from src.database.base_repository import BaseRepository
from src.models.hashtag import Hashtag


class HashtagRepository(BaseRepository):

    def get_hashtag(self, text: str) -> Hashtag:
        response = self.execute_query_one(
            "SELECT * FROM hashtag WHERE text = ?", (text,)
        )
        if response:
            return Hashtag(
                id=response["id"],
                challenge_id=response["challenge_id"],
                last_fetched_cursor=response["last_fetched_cursor"],
                has_more=response["has_more"],
                text=response["text"],
                view_count=response["view_count"],
                video_count=response["video_count"],
            )

    def create_hashtag(self, hashtag: Hashtag):
        return self.execute_query(
            "INSERT INTO hashtag (text, challenge_id, last_fetched_cursor, has_more, view_count, video_count) VALUES (?, ?, ?, ?, ?, ?)",
            (
                hashtag.text,
                hashtag.challenge_id,
                hashtag.last_fetched_cursor,
                hashtag.has_more,
                hashtag.view_count,
                hashtag.video_count,
            ),
        )

    def update_hashtag(self, last_fetched_cursor: str, has_more: bool, text: str):
        return self.execute_query(
            "UPDATE hashtag SET last_fetched_cursor = ?, has_more = ? WHERE text = ?",
            (
                last_fetched_cursor,
                has_more,
                text,
            ),
        )
