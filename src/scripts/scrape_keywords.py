import asyncio
import random
from src.database.author_repository import AuthorRepository
from src.database.keyword_repository import KeywordRepository
from src.database.video_repository import VideoRepository
from src.models.keyword import Keyword
from src.models.user import User
from src.models.video import Video
from src.tiktok_api.api import TikTokApi
from src.tiktok_api.models import TikTokVideoListResponse


class ScrapeKeyword:
    def __init__(self, tiktok_api: TikTokApi):
        self.tiktok_api = tiktok_api
        self.keyword_repository = KeywordRepository()
        self.video_repository = VideoRepository()
        self.author_repository = AuthorRepository()

    @classmethod
    async def initialize(cls):
        tiktok_api = await TikTokApi.initialize()
        return cls(tiktok_api)

    def save_data(
        self,
        data: TikTokVideoListResponse,
        keyword: Keyword,
        isKeywordExist: bool = True,
    ):
        if isKeywordExist:
            self.keyword_repository.update_keyword(keyword)
        else:
            self.keyword_repository.insert_keyword(keyword)

        keyword_id = self.keyword_repository.get_keyword_by_text(keyword.text).id

        for video in data.videos:
            if self.video_repository.get_video_by_tiktok_video_id(video.get("id")):
                return
            video_author = video.get("author", {})
            video_author_stats = video.get("authorStats", {})
            author = User(
                tiktok_unique_id=video_author.get("uniqueId"),
                sec_uid=video_author.get("secUid"),
                follower_count=video_author_stats.get("followerCount"),
                following_count=video_author_stats.get("followingCount"),
                video_count=video_author_stats.get("videoCount"),
                like_count=video_author_stats.get("heartCount"),
            )
            existing_author = self.author_repository.get_author(author.tiktok_unique_id)
            author_id = (
                self.author_repository.create_author(author)
                if not existing_author
                else existing_author.id
            )
            video_stats = video.get("stats", {})
            self.video_repository.create_video(
                video=Video(
                    tiktok_video_id=video.get("id"),
                    hashtag_id=None,
                    author_id=author_id,
                    author_username=author.tiktok_unique_id,
                    keyword_id=keyword_id,
                    comment_count=int(video_stats.get("commentCount")),
                    like_count=int(video_stats.get("diggCount")),
                    view_count=int(video_stats.get("playCount")),
                    video_url=f"https://www.tiktok.com/@{author.tiktok_unique_id}/video/{video.get('id')}",
                    description=video.get("desc"),
                )
            )

    async def scrape(
        self,
        keyword_text: str,
    ):
        existing_keyword = self.keyword_repository.get_keyword_by_text(keyword_text)
        search_id, offset = None, 0
        count = 1
        print(f"Scraping {keyword_text} #{count}")
        if existing_keyword:
            search_id = existing_keyword.search_id
            offset = existing_keyword.last_fetched_cursor
        data = await self.tiktok_api.get_keyword_videos(keyword_text, offset, search_id)
        if existing_keyword:
            existing_keyword.last_fetched_cursor = data.cursor
            existing_keyword.has_more = data.has_more
            self.save_data(data, existing_keyword, isKeywordExist=True)
        else:
            keyword = Keyword(
                text=keyword_text,
                last_fetched_cursor=data.cursor,
                search_id=data.search_id,
                has_more=data.has_more,
            )
            self.save_data(data, keyword, False)
        count += 1
        while data.has_more and count < 11:
            await asyncio.sleep(random.randint(2, 4))
            print(f"Scraping {keyword_text} #{count}")
            count += 1
            offset = data.cursor
            data = await self.tiktok_api.get_keyword_videos(
                keyword_text, offset, search_id
            )
            print(f"found {len(data.videos)} videos in {keyword_text} #{count}")
            keyword = self.keyword_repository.get_keyword_by_text(keyword_text)
            keyword.last_fetched_cursor = data.cursor
            keyword.has_more = data.has_more
            self.save_data(data, keyword)

        print(f"Finishing Scraping for {keyword_text} #{count}")


async def run():
    scrape_keyword = await ScrapeKeyword.initialize()
    keywords = [
        "beautiful destinations",
        "places to visit",
        "places to travel",
        "places that don't feel real",
        "travel hacks",
    ]
    tasks = []
    for keyword in keywords:
        tasks.append(asyncio.create_task(scrape_keyword.scrape(keyword)))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run())
