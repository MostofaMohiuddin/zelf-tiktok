import json
import os
import urllib
import urllib.parse
from urllib.parse import urlparse, parse_qs, quote
import httpx
from tenacity import retry, stop_after_attempt

from src.tiktok_api.models import TikTokCommentListResponse, TikTokVideoListResponse
from src.tiktok_api.tiktok_signature_generator import TikTokSignatureGenerator


class TikTokApi:
    def __init__(
        self,
        tiktok_signature_generator: TikTokSignatureGenerator,
        httpx_client: httpx.AsyncClient,
        authenticated_httpx_client: httpx.AsyncClient,
    ):
        self.tiktok_signature_generator = tiktok_signature_generator
        self.httpx_client = httpx_client
        self.authenticated_httpx_client = authenticated_httpx_client
        self.base_url = "https://www.tiktok.com/api"
        self.common_query_params = {
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "battery_info": "0.54",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "MacIntel",
            "browser_version": "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": "7195820289077478917",
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "hashtag",
            "history_len": "5",
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": "en",
            "os": "mac",
            "priority_region": "BD",
            "referer": "https://www.tiktok.com/business-suite/messages?from=homepage&lang=en",
            "region": "BD",
            "root_referer": "https://www.tiktok.com/business-suite/messages?from=homepage&lang=en",
            "screen_height": "1120",
            "screen_width": "1792",
            "tz_name": "Asia/Dhaka",
            "webcast_language": "en",
            "msToken": "CpV2ORgO8iTt_ecdH_eggfhBqxpA-3U3YiAYPw8Z88YVxLYUBeFJj4ajqBhXOf73nuEW2rKz-hRVOi4U9Tx8ZoK5mourhNQaxgVpqwpjhqowzK08vxw4_DWbreQuOsJpgzpIk5TTfLtxiD8Za0WYavnWAA==",
        }

    @classmethod
    @retry(stop=stop_after_attempt(3))
    async def initialize(cls):
        tiktok_signature_generator = await TikTokSignatureGenerator.initialize()
        device_info = await tiktok_signature_generator.device_info()
        httpx_client = httpx.AsyncClient(
            headers={
                "User-Agent": device_info.get("user_agent"),
            }
        )
        cookie_header = None
        with open(os.path.join(os.path.dirname(__file__), "cookies.json"), "r") as f:
            cookies = json.load(f)
            cookie_header = "; ".join(
                [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
            )
        authenticated_httpx_client = httpx.AsyncClient(
            headers={
                "User-Agent": device_info.get("user_agent"),
                "Cookie": cookie_header,
                "tt-csrf-token": "CaNyFQKY-6sa8O30_ieYFrXAZh89vdPoKGZY",
                "tt-ticket-guard-client-data": "eyJ0c19zaWduIjoidHMuMS40M2FmOTU1OGU4YjMxMGFjYjc4Y2JjYTM3Y2RkMGE4YWU3ODI2ZjE3MGM1ZmYyZWU0NDY4YzYwZTkyODAxNGQ4MGU3MGI0YmRhODJjMTM4MzZlNWNmYTE4Mzk0ZDcwMjQwZjhhZjE2MzFmMTY1YWU5NjAxMjJlZWZmZDQ1MzNkZCIsInJlcV9jb250ZW50IjoidGlja2V0LHBhdGgsdGltZXN0YW1wIiwicmVxX3NpZ24iOiJNRVFDSUMxaC9jaDEwVFp4Vk85QVFuRnVQZTJlM1ZMVEJvSXhHVE13RmR6VTVsckRBaUFkNDZkUldZejFWbm5Hd2pBVWFSaGp4V3dQb3V4NUpNV1FHVnJ2UDdMVEdBPT0iLCJ0aW1lc3RhbXAiOjE3MjgxMTM2MjN9",
                "tt-ticket-guard-iteration-version": "0",
                "tt-ticket-guard-public-key": "BGu7I/olJcxXM5cUUXfEa/VqZ/T1E1BOXDNz77ZqflZHWs70ocSgWP6OCyQabEG15QOm6aoE2K1ickIBPCKy8Ys=",
                "tt-ticket-guard-version": "2",
                "tt-ticket-guard-web-version": "1",
                "x-secsdk-csrf-token": "000100000001d613aa36787ca4371478f961d129b5bdb910cb8951cd91959ccf339e2cf7f52f17fb7e2f64d4f3c7",
            },
        )
        return cls(tiktok_signature_generator, httpx_client, authenticated_httpx_client)

    async def close(self):
        await self.tiktok_signature_generator.close()
        await self.httpx_client.aclose()

    @retry(stop=stop_after_attempt(3))
    async def like_video(self, video_id: str):
        query_params = {
            **self.common_query_params,
            "aweme_id": video_id,
            "user_is_login": "true",
            "type": "1",
        }
        url = f"{self.base_url}/commit/item/digg/?" + urllib.parse.urlencode(
            query_params
        )
        signed_url = await self.tiktok_signature_generator.sign_url(url)
        response = await self.authenticated_httpx_client.post(signed_url)
        print(response.status_code)

    @retry(stop=stop_after_attempt(3))
    async def get_comments(self, video_id: str, cursor: str = "0"):
        query_params = {
            **self.common_query_params,
            "aweme_id": video_id,
            "cursor": cursor,
            "count": 20,
            "user_is_login": "true",
        }
        url = f"{self.base_url}/comment/list/?" + urllib.parse.urlencode(query_params)
        signed_url = await self.tiktok_signature_generator.sign_url(url)
        response = await self.authenticated_httpx_client.get(signed_url)
        data = response.json()
        return TikTokCommentListResponse(
            comments=data.get("comments", []),
            cursor=str(data.get("cursor", 0)),
            has_more=data.get("has_more", False),
        )

    @retry(stop=stop_after_attempt(3))
    async def comment_video(self, video_id: str, comment: str):
        data = await self.authenticated_httpx_client.head(
            f"{self.base_url}/comment/publish/"
        )

        query_params = {
            **self.common_query_params,
            "aweme_id": video_id,
            "user_is_login": "true",
            "text": comment,
            "text_extra": "[]",
            "WebIdLastTime": "1726937089",
            "odinId": "7379754163306005521",
        }
        url = f"{self.base_url}/comment/publish/?" + urllib.parse.urlencode(
            query_params
        )
        signed_url = await self.tiktok_signature_generator.sign_url(url)
        response = await self.authenticated_httpx_client.post(signed_url)
        print(response.status_code)

    @retry(stop=stop_after_attempt(3))
    async def get_challenge_info(self, challenge_name: str):
        query_params = {
            **self.common_query_params,
            "challengeName": challenge_name,
        }
        url = f"{self.base_url}/challenge/detail/?" + urllib.parse.urlencode(
            query_params
        )
        signed_url = await self.tiktok_signature_generator.sign_url(url)
        response = await self.httpx_client.get(signed_url)
        return response.json()

    @retry(stop=stop_after_attempt(3))
    async def get_hashtag_videos(
        self, challenge_id: str, cursor: str = "0"
    ) -> TikTokVideoListResponse:
        query_params = {
            **self.common_query_params,
            "challengeID": challenge_id,
            "cursor": cursor,
            "count": 30,
        }
        url = f"{self.base_url}/challenge/item_list/?" + urllib.parse.urlencode(
            query_params
        )
        signed_url = await self.tiktok_signature_generator.sign_url(url)
        response = await self.httpx_client.get(signed_url)
        data = response.json()
        return TikTokVideoListResponse(
            videos=data.get("itemList", []),
            cursor=data.get("cursor", 0),
            has_more=data.get("hasMore", False),
        )

    @retry(stop=stop_after_attempt(3))
    async def get_keyword_videos(
        self, keyword: str, offset: int = 0, search_id: str = None
    ):
        query_params = {
            **self.common_query_params,
            "count": 20,
            "user_is_login": "true",
            "offset": offset,
            # "web_search_code": '{"tiktok":{"client_params_x":{"search_engine":{"ies_mt_user_live_video_card_use_libra":1,"mt_search_general_user_live_card":1}},"search_server":{}}}',
            # "webIdLastTime": "1726937089",
        }

        if offset != 0:
            query_params["search_id"] = search_id
        url = (
            f"{self.base_url}/search/item/full/?{urllib.parse.urlencode(query_params)}"
            + f"&keyword={quote(keyword)}"
        )
        # url2 = """https://www.tiktok.com/api/search/item/full/?WebIdLastTime=1726937089&aid=1988&app_language=en&app_name=tiktok_web&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F129.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&count=20&data_collection_enabled=true&device_id=7417138275792176647&device_platform=web_pc&focus_state=false&from_page=search&history_len=7&is_fullscreen=true&is_page_visible=true&keyword=beautiful%27s%20view&odinId=7379754163306005521&offset=12&os=mac&priority_region=BD&referer=&region=BD&screen_height=1117&screen_width=1728&search_id=20241004180115BF0042A89E3CCEF4827A&tz_name=Asia%2FDhaka&user_is_login=true&verifyFp=verify_m1chtiwy_rM2sSUSe_RSTf_4sS3_Aifi_gjVma5fzKpI7&web_search_code=%7B%22tiktok%22%3A%7B%22client_params_x%22%3A%7B%22search_engine%22%3A%7B%22ies_mt_user_live_video_card_use_libra%22%3A1%2C%22mt_search_general_user_live_card%22%3A1%7D%7D%2C%22search_server%22%3A%7B%7D%7D%7D&webcast_language=en&msToken=ETn_REfLWzdn98mCGmPm03S3j6w3Cu8Vy0SFF9ISAElPEvwQvEFxbte7UPLh3dxykQLDsM-AzEfo4msUw3YgPkFd7mc276XzV_qxOk-chLz0FtsveFuvzidakV8x1sJmhgHbuqvx5PT1_XGJMoD20iut4g==&X-Bogus=DFSzswVY0e0ANj1qtB3yR5Im4L7b&_signature=_02B4Z6wo00001VbM3WAAAIDAtgcWswcokNFWzNnAADK21c"""
        signed_url = await self.tiktok_signature_generator.sign_url(url)

        response = await self.authenticated_httpx_client.get(signed_url)
        data = response.json()
        return TikTokVideoListResponse(
            videos=data.get("item_list", []),
            cursor=str(data.get("cursor", 0)),
            has_more=data.get("has_more", False),
            search_id=data.get("extra", {}).get("logid"),
        )
