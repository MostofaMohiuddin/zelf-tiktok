from src.database.base_repository import BaseRepository
from src.models.user import User


class AuthorRepository(BaseRepository):

    def get_author(self, tiktok_unique_id: str) -> User:
        response = self.execute_query_one(
            "SELECT * FROM user WHERE tiktok_unique_id = ?", (tiktok_unique_id,)
        )
        if response:
            return User(
                id=response["id"],
                tiktok_unique_id=response["tiktok_unique_id"],
                sec_uid=response["sec_uid"],
                follower_count=response["follower_count"],
                following_count=response["following_count"],
                video_count=response["video_count"],
                like_count=response["like_count"],
            )

    def create_author(self, author: User) -> int:
        return self.execute_query(
            "INSERT INTO user (tiktok_unique_id, sec_uid, follower_count, following_count, video_count, like_count) VALUES (?, ?, ?, ?, ?, ?)",
            (
                author.tiktok_unique_id,
                author.sec_uid,
                author.follower_count,
                author.following_count,
                author.video_count,
                author.like_count,
            ),
        )

    def get_influencer(self) -> list[User]:
        follower_count = 100000
        like_count = 1000000
        query = "SELECT * FROM user WHERE follower_count > ? and like_count > ? ORDER BY like_count DESC, follower_count DESC"
        response = self.execute_query(query, (follower_count, like_count))
        if not response:
            return []
        return [
            User(
                id=user["id"],
                tiktok_unique_id=user["tiktok_unique_id"],
                sec_uid=user["sec_uid"],
                follower_count=user["follower_count"],
                following_count=user["following_count"],
                video_count=user["video_count"],
                like_count=user["like_count"],
            )
            for user in response
        ]
