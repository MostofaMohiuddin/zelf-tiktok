import asyncio
import time

from src.tiktok_api.api import TikTokApi


async def init():
    tiktok_api = await TikTokApi.initialize()

    data = await tiktok_api.get_keyword_videos("beautiful's view", offset=0)
    print(data.cursor)
    print(data.videos[0].get("desc"))
    print(data.has_more)
    print(len(data.videos))
    print(data.search_id)


if __name__ == "__main__":
    asyncio.run(init())
