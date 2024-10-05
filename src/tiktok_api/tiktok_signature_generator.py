import os
from playwright.async_api import async_playwright, Page

import urllib.parse


class TikTokSignatureGenerator:
    def __init__(self, page: Page, playwright):
        self.page = page
        self.playwright = playwright

    @classmethod
    async def initialize(cls):
        args = [
            "--disable-blink-features",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--window-size=1920,1080",
            "--start-maximized",
        ]
        default_url = "https://www.tiktok.com/"

        # async with async_playwright() as playwright:
        playwright = await async_playwright().start()
        iphone_13 = playwright.devices["iPhone 13"]
        browser = await playwright.chromium.launch(
            headless=True,
            args=args,
            ignore_default_args=["--mute-audio", "--hide-scrollbars"],
        )
        context = await browser.new_context(
            **iphone_13,
            locale="en-US",
            bypass_csp=True,
        )
        page = await context.new_page()
        await page.route(
            "**/*",
            lambda route: (
                route.abort()
                if route.request.resource_type == "script"
                else route.continue_()
            ),
        )
        await page.goto(default_url, wait_until="networkidle")

        scripts_to_load = ["signer.js", "webmssdk.js", "xbogus.js"]
        for script in scripts_to_load:
            await page.add_script_tag(
                path=os.path.join(os.path.dirname(__file__), "js_scripts", script)
            )

        await page.evaluate(
            """() => {                    
            window.generate_signature = function generateSignature(url) {
                        if (typeof window.byted_acrawler.sign !== "function") {
                        throw "No signature function found";
                        }
                        return window.byted_acrawler.sign({ url: url });
                    };

                window.generate_bogus = function generateBogus(query, user_agent) {
                
                    if (typeof window.generateBogus !== "function") {
                    throw "No X-Bogus function found";
                    }
                    return window.generateBogus(query, user_agent);
                };
                }
            """
        )
        return cls(page, playwright)

    async def device_info(self):
        info = await self.page.evaluate(
            """() => {
            return {
                deviceScaleFactor: window.devicePixelRatio,
                user_agent: window.navigator.userAgent,
                browser_language: window.navigator.language,
                browser_platform: window.navigator.platform,
                browser_name: window.navigator.appCodeName,
                browser_version: window.navigator.appVersion,
            };
        }
        """
        )
        return info

    async def generate_signature(self, url: str):
        signature = await self.page.evaluate(f"window.generate_signature('{url}')")
        return signature

    async def generate_bogus(self, url: str, user_agent: str):
        query = urllib.parse.urlparse(url).query
        bogus = await self.page.evaluate(
            f"window.generate_bogus('{query}', '{user_agent}')"
        )
        return bogus

    async def sign_url(self, url: str):
        verify_fp = "verify_5b161567bda98b6a50c0414d99909d4b"
        url = f"{url}&verifyFp={verify_fp}"
        signature = await self.generate_signature(url)
        signed_url = f"{url}&_signature={signature}"
        user_agent = await self.page.evaluate("() => window.navigator.userAgent")
        bogus = await self.generate_bogus(signed_url, user_agent)
        signed_url = f"{signed_url}&X-Bogus={bogus}"
        return signed_url

    async def close(self):
        await self.playwright.stop()
