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
        self.authorized = os.getenv("AUTHORIZED_DATA_SOURCE", "false").lower() == "true"
        self.timeout = int(os.getenv("HTTP_TIMEOUT", "20"))
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/json",
            "User-Agent": "ZillowAgentResearchClient/1.0 (configure authorized provider)",
        })

    def fetch_html(self, url):
        if not self.authorized:
            raise RuntimeError(
                "Data fetching disabled. Confirm provider authorization and set "
                "AUTHORIZED_DATA_SOURCE=true in .env."
            )
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text
