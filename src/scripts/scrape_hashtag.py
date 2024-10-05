import asyncio
import random
import time
from src.database.author_repository import AuthorRepository
from src.database.hashtag_repository import HashtagRepository
from src.database.keyword_repository import KeywordRepository
from src.database.video_repository import VideoRepository
from src.models.hashtag import Hashtag
from src.models.keyword import Keyword
from src.models.user import User
from src.models.video import Video
from src.tiktok_api.api import TikTokApi
from src.tiktok_api.models import TikTokVideoListResponse


class ScrapeHashtag:
    def __init__(self, tiktok_api: TikTokApi):
        self.tiktok_api = tiktok_api
        self.hashtag_repository = HashtagRepository()
        self.video_repository = VideoRepository()
        self.author_repository = AuthorRepository()

    @classmethod
    async def initialize(cls):
        tiktok_api = await TikTokApi.initialize()
        return cls(tiktok_api)

    def save_data(
        self,
        data: TikTokVideoListResponse,
        hashtag: Hashtag,
        isHashtagExist: bool = True,
    ):
        if isHashtagExist:
            self.hashtag_repository.update_hashtag(
                hashtag.last_fetched_cursor, hashtag.has_more, hashtag.text
            )
        else:
            self.hashtag_repository.create_hashtag(hashtag)

        hashtag_id = self.hashtag_repository.get_hashtag(hashtag.text).id

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
                    hashtag_id=hashtag_id,
                    author_id=author_id,
                    author_username=author.tiktok_unique_id,
                    keyword_id=None,
                    comment_count=int(video_stats.get("commentCount")),
                    like_count=int(video_stats.get("diggCount")),
                    view_count=int(video_stats.get("playCount")),
                    video_url=f"https://www.tiktok.com/@{author.tiktok_unique_id}/video/{video.get('id')}",
                    description=video.get("desc"),
                )
            )

    async def scrape(
        self,
        hashtag_text: str,
    ):
        count = 1
        print(f"Scraping {hashtag_text} #{count}")
        existing_hashtag = self.hashtag_repository.get_hashtag(hashtag_text)
        challenge_id, cursor = None, 0
        challenge_info = None
        if existing_hashtag:
            challenge_id = existing_hashtag.challenge_id
            cursor = existing_hashtag.last_fetched_cursor
        else:
            challenge_info = await self.tiktok_api.get_challenge_info(hashtag_text)
            challenge_id = (
                challenge_info.get("challengeInfo", {}).get("challenge", {}).get("id")
            )
        data = await self.tiktok_api.get_hashtag_videos(challenge_id, cursor)
        if existing_hashtag:
            existing_hashtag.last_fetched_cursor = data.cursor
            existing_hashtag.has_more = data.has_more
            self.save_data(data, existing_hashtag, isHashtagExist=True)
        else:
            hashtag = Hashtag(
                text=hashtag_text,
                last_fetched_cursor=data.cursor,
                challenge_id=challenge_id,
                has_more=data.has_more,
                video_count=int(
                    challenge_info.get("challengeInfo", {})
                    .get("statsV2", {})
                    .get("videoCount")
                ),
                view_count=int(
                    challenge_info.get("challengeInfo", {})
                    .get("statsV2", {})
                    .get("viewCount")
                ),
            )
            self.save_data(data, hashtag, isHashtagExist=False)
        count += 1
        while data.has_more and count < 11:
            print(f"Scraping {hashtag_text} #{count}")
            count += 1
            await asyncio.sleep(random.randint(2, 4))
            data = await self.tiktok_api.get_hashtag_videos(challenge_id, cursor)
            print(f"found {len(data.videos)} videos in {hashtag_text} #{count}")
            hashtag = self.hashtag_repository.get_hashtag(hashtag_text)
            hashtag.last_fetched_cursor = data.cursor
            hashtag.has_more = data.has_more
            cursor = data.cursor
            self.save_data(data, hashtag)

        print(f"Finishing Scraping for {hashtag_text} #{count}")


async def run():
    scrape_hashtag = await ScrapeHashtag.initialize()
    tags = [
        "traveltok",
        "wanderlust",
        "backpackingadventures",
        "luxurytravel",
        "hiddengems",
        "solotravel",
        "roadtripvibes",
        "travelhacks",
        "foodietravel",
        "sustainabletravel",
    ]
    tasks = []
    for tag in tags:
        tasks.append(asyncio.create_task(scrape_hashtag.scrape(tag)))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run())
