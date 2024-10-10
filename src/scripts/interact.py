import asyncio
from src.tiktok_api.api import TikTokApi
from urllib.parse import urlparse

USER_UNIQUE_ID = "john.doe0343"
COMMENT_TEXT = "This is a comment"


class Interact:
    def __init__(self, tiktok_api: TikTokApi):
        self.tiktok_api = tiktok_api

    @classmethod
    async def initialize(cls):
        tiktok_api = await TikTokApi.initialize()
        return cls(tiktok_api)

    async def like_video(self, url: str):
        parsed_url = urlparse(url)
        video_id = parsed_url.path.split("/")[-1]
        await self.tiktok_api.like_video(video_id)

    async def comment_video(self, url: str, comment: str):
        parsed_url = urlparse(url)
        video_id = parsed_url.path.split("/")[-1]
        await self.tiktok_api.comment_video(video_id, comment)

    def found_comment(self, comments: dict, user_unique_id: str, text: str):
        for comment in comments:
            comment_text = comment.get("text", "")
            user = comment.get("user", {})
            if user.get("unique_id") == user_unique_id and text == comment_text:
                return True
        return False

    async def verify_comment(self, url: str, user_id: str, text: str):
        await asyncio.sleep(5)  # Wait for the comment to be posted
        count = 0
        parsed_url = urlparse(url)
        video_id = parsed_url.path.split("/")[-1]
        data = await self.tiktok_api.get_comments(video_id, "0")
        if self.found_comment(data.comments, user_id, text):
            print("Comment found")
            return True
        while data.has_more and count < 10:
            await asyncio.sleep(1)
            count += 1
            data = await self.tiktok_api.get_comments(video_id, data.cursor)
            if self.found_comment(data.comments, user_id, text):
                print("Comment found")
                return True
        print("Comment Not found")


async def run():
    interact = await Interact.initialize()
    await interact.like_video(
        "https://www.tiktok.com/@banglavision/video/7418587332263120146"
    )
    await interact.comment_video(
        "https://www.tiktok.com/@banglavision/video/7418587332263120146",
        COMMENT_TEXT,
    )
    await interact.verify_comment(
        "https://www.tiktok.com/@banglavision/video/7418587332263120146",
        USER_UNIQUE_ID,
        COMMENT_TEXT,
    )


if __name__ == "__main__":
    asyncio.run(run())
