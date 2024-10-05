from src.database.base_repository import BaseRepository
from src.models.video import Video


class VideoRepository(BaseRepository):
    def get_videos_by_keyword_id(self, keyword_id) -> list[Video]:
        query = "SELECT * FROM video WHERE keyword_id = ?"
        response = self.execute_many_query(query, (keyword_id,))
        return [
            Video(
                id=video["id"],
                tiktok_video_id=video["tiktok_video_id"],
                hashtag_id=video["hashtag_id"],
                keyword_id=video["keyword_id"],
                author_username=video["author_username"],
                author_id=video["author_id"],
                like_count=video["like_count"],
                view_count=video["view_count"],
                video_url=video["video_url"],
                description=video["description"],
            )
            for video in response
        ]

    def get_video_by_tiktok_video_id(self, tiktok_video_id) -> Video:
        query = "SELECT * FROM video WHERE tiktok_video_id = ?"
        response = self.execute_query_one(query, (tiktok_video_id,))
        if response:
            return Video(
                id=response["id"],
                tiktok_video_id=response["tiktok_video_id"],
                hashtag_id=response["hashtag_id"],
                keyword_id=response["keyword_id"],
                author_username=response["author_username"],
                author_id=response["author_id"],
                like_count=response["like_count"],
                view_count=response["view_count"],
                video_url=response["video_url"],
                description=response["description"],
            )

    def create_video(self, video: Video):
        if self.get_video_by_tiktok_video_id(video.tiktok_video_id):
            return
        query = """
            INSERT INTO video (
                tiktok_video_id,
                hashtag_id,
                keyword_id,
                author_username,
                author_id,
                like_count,
                view_count,
                video_url,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(
            query,
            (
                video.tiktok_video_id,
                video.hashtag_id,
                video.keyword_id,
                video.author_username,
                video.author_id,
                video.like_count,
                video.view_count,
                video.video_url,
                video.description,
            ),
        )
