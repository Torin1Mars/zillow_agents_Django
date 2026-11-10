import os
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class AuthorizedPageFetcher:
    """
    HTTP adapter for a data source that explicitly authorizes this collection.
    The response must expose the page payload expected by the parsers.
    """
    def __init__(self):
        self.authorized = (
                os.getenv("AUTHORIZED_DATA_SOURCE", "false").lower() == "true"
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Referer": "https://www.google.com/",
        }

        self.timeout = int(os.getenv("HTTP_TIMEOUT", "20"))
        self.session = requests.Session()

        self.session.headers.update(self.headers)


    def reset_session(self):
        self.session.close()
        #New session
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        logger.info(
           msg = "SESSION HAS BEEN RESET")

    def fetch_html(self, url):
        if not self.authorized:
            raise RuntimeError("Data fetching is disabled.")

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()
        logger.info("Request successful: %s", url)
        return response.text