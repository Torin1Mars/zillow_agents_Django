import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class GeneralCardsParser:
    """Parses paginated agent-directory results from a compatible HTML payload."""

    def __init__(self, fetcher, delay_range=(1, 6)):
        self.fetcher = fetcher
        self.delay_range = delay_range

    def parse_location(self, url_template, location):
        from urllib.parse import quote
        import random
        import time

        url = url_template.format(location=quote(location))
        html = self.fetcher.fetch_html(url)
        pages = self.check_pages_count(html)
        agents = self.parse_agents(self.extract_data(html))

        for page_number in range(2, pages + 1):
            time.sleep(random.randint(*self.delay_range))
            page_url = f"{url}{'&' if '?' in url else '?'}page={page_number}"
            page_html = self.fetcher.fetch_html(page_url)
            agents.extend(self.parse_agents(self.extract_data(page_html)))
            logger.info("Location %s: parsed page %s/%s", location, page_number, pages)

        logger.info("Location %s: collected %s short agent cards", location, len(agents))
        return agents

    @staticmethod
    def extract_data(html):
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("script", id="__NEXT_DATA__")
        if tag is None:
            raise RuntimeError("__NEXT_DATA__ not found in compatible source response")
        return json.loads(tag.get_text())

    @staticmethod
    def check_pages_count(html):
        soup = BeautifulSoup(html, "html.parser")
        readout = soup.select_one('li[class*="PaginationReadoutItem"] span')
        if readout is None:
            return 1
        try:
            return int(readout.get_text().split("of")[-1].strip().replace(",", ""))
        except (ValueError, AttributeError):
            logger.warning("Could not determine pagination count; processing first page only")
            return 1

    def parse_agents(self, data):
        finder = (
            data.get("props", {}).get("pageProps", {})
                .get("displayData", {}).get("agentDirectoryFinderDisplay", {})
        )
        cards = (
            finder.get("searchResults", {}).get("results", {}).get("resultsCards", [])
        )
        result = []
        for card in cards:
            if card.get("__typename") == "AgentDirectoryFinderProfileResultsCard":
                result.append(self.parse_card(card))
        return result

    @staticmethod
    def parse_card(card):
        review = card.get("reviewInformation") or {}
        profile_data = card.get("profileData") or []
        sales_12m = 0
        for item in profile_data:
            if "last 12 months" in str(item.get("label", "")).lower():
                try:
                    sales_12m = int(item.get("formattedData") or 0)
                except (TypeError, ValueError):
                    sales_12m = 0
                break
        return {
            "name": card.get("cardTitle"),
            "brokerage": (card.get("secondaryCardTitle") or "").strip(),
            "url": card.get("cardActionLink"),
            "rating": review.get("reviewAverage"),
            "reviews": review.get("reviewCount"),
            "top_agent": bool(card.get("isTopAgent")),
            "team": any(t.get("text") == "TEAM" for t in card.get("tags", [])),
            "sales_12m": sales_12m,
        }
