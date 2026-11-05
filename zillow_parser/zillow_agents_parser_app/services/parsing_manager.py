import csv
import logging
import os
import time
from pathlib import Path
from django.conf import settings
from zillow_agents_parser_app.parsers.page_fetcher import AuthorizedPageFetcher
from zillow_agents_parser_app.parsers.general_cards_parser import GeneralCardsParser
from zillow_agents_parser_app.parsers.internal_agent_parser import InternalAgentParser
from .agent_saver import save_agent

logger = logging.getLogger(__name__)

class ParsingManager:
    def __init__(self):
        self.fetcher = AuthorizedPageFetcher()
        delay = (
            int(os.getenv("PARSER_DELAY_MIN", "1")),
            int(os.getenv("PARSER_DELAY_MAX", "6")),
        )
        self.general_parser = GeneralCardsParser(self.fetcher, delay)
        self.profile_parser = InternalAgentParser(self.fetcher, delay)

    @staticmethod
    def load_locations(locationPostIndexKey :str)->list:
        path = Path(settings.BASE_DIR) / "zillow_agents_parser_app" / "searching_locations" / "us_zipcodes.csv"

        checking_post_codes = []
        if not path.exists():
            return []


        with open(path, mode="r", encoding="Utf-8") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row)>2 and row[2]==locationPostIndexKey:
                    checking_post_codes.append(row[0])

        logger.warning(f"Will need to check {len(checking_post_codes)} postcodes.")
        return checking_post_codes

    def run_once(self):
        template = os.getenv("ZILLOW_SEARCH_URL_TEMPLATE", "").strip()
        if not template or "{location}" not in template:
            raise RuntimeError("Set ZILLOW_SEARCH_URL_TEMPLATE in .env; it must contain {location}.")

        post_index_key = os.getenv("SEARCH_POST_INDEX_KEY", "").strip()
        locations = self.load_locations(post_index_key)
        if not locations:
            logger.warning("No search locations configured in sources/search_locations.txt")
            return

        total_found = created = updated = failed = 0
        for location in locations:
            logger.info("STAGE 1 — general cards for location: %s", location)
            cards = self.general_parser.parse_location(template, location)
            total_found += len(cards)

            logger.info("STAGE 2 — internal profiles: %s cards", len(cards))
            for index, card in enumerate(cards, start=1):
                profile_url = card.get("url")
                if not profile_url:
                    failed += 1
                    logger.warning("[%s/%s] Skipping card without profile URL", index, len(cards))
                    continue
                try:
                    logger.info("[%s/%s] Parsing profile: %s", index, len(cards), profile_url)
                    payload = self.profile_parser.parse_profile(profile_url)
                    _, was_created = save_agent(card, payload)
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception:
                    failed += 1
                    logger.exception("Profile failed; continuing with next card: %s", profile_url)

        logger.info(
            "PARSING SUMMARY | cards=%s created=%s updated=%s failed=%s",
            total_found, created, updated, failed,
        )

    def run_forever(self, pause_seconds=300):
        while True:
            try:
                self.run_once()
            except Exception:
                logger.exception("Parsing cycle failed")
            logger.info("Next parsing cycle in %s seconds", pause_seconds)
            time.sleep(pause_seconds)
