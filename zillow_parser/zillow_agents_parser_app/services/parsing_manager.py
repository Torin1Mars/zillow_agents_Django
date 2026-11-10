import csv
import logging
import os
import random
import time
from pathlib import Path
from string import capwords

import requests
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
        self.sleep_for_restart = 20

    @staticmethod
    def load_locations(locationPostIndexKey :str)->list:
        path = Path(settings.BASE_DIR) / "zillow_agents_parser_app" / "searching_locations" / "us_zipcodes.csv"

        checking_post_codes = []
        if not path.exists():
            return []

        #Getting post codes from locations file list
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
            raise RuntimeError(
                "Set ZILLOW_SEARCH_URL_TEMPLATE in .env; "
                "it must contain {location}."
            )

        post_index_key = os.getenv("SEARCH_POST_INDEX_KEY", "").strip()
        locations = self.load_locations(post_index_key)

        if not locations:
            logger.warning("No search locations configured in us_zipcodes.csv")
            return

        total_found = created = updated = failed = 0

        for location in locations:
            logger.info("STAGE 1 — general cards for location: %s", location)

            cards = self.general_parser.parse_location(template, location)
            total_found += len(cards)

            logger.info("STAGE 2 — internal profiles: %s cards", len(cards))

            #EXPERIMENTAL
            split_index = random.randint(0, len(cards))

            #Splitiong profiles on two half's and swapping general agents profiles list
            part_1 = cards[:split_index]
            part_2 = cards[split_index:]
            cards = part_2 + part_1

            for index, card in enumerate(cards, start=1):
                profile_url = card.get("url")

                if not profile_url:
                    failed += 1
                    logger.warning(
                        "[%s/%s] Skipping card without profile URL",
                        index, len(cards)
                    )
                    continue

                while True:
                    try:
                        logger.info(
                            "[%s/%s] Parsing profile: %s",
                            index, len(cards), profile_url
                        )

                        payload = self.profile_parser.parse_profile(profile_url)
                        _, was_created = save_agent(card, payload)

                        if was_created:
                            created += 1
                        else:
                            updated += 1

                        break

                    except requests.HTTPError as exc:
                        status_code = (
                            exc.response.status_code
                            if exc.response is not None
                            else None
                        )

                        if status_code in (403, 429, 503):
                            logger.warning(
                                "Blocking response HTTP %s for %s. "
                                "Waiting 60 seconds before retry.",
                                status_code,
                                profile_url,
                            )
                            self.fetcher.reset_session()

                            time.sleep(self.sleep_for_restart)
                            continue

                        failed += 1
                        logger.exception(
                            "Profile failed: %s", profile_url
                        )
                        break

                    except Exception:
                        failed += 1
                        logger.exception(
                            "Profile failed: %s", profile_url
                        )
                        break

        logger.info(
            "PARSING SUMMARY | cards=%s created=%s updated=%s failed=%s",
            total_found, created, updated, failed,
        )


    def run_forever(self, parsing_cycle_delay=300):
        while True:
            try:
                self.run_once()

            except requests.HTTPError as exc:
                status_code = (
                    exc.response.status_code
                    if exc.response is not None
                    else None
                )

                if status_code in (403, 429, 503):
                    logger.warning(
                        "Blocking response HTTP %s. "
                        "Waiting before retrying parsing cycle.",
                        status_code,
                    )
                    time.sleep(self.sleep_for_restart)
                    continue

                logger.exception("Parsing cycle failed")

            except Exception:
                logger.exception("Parsing cycle failed")

            logger.info("Next parsing cycle in %s seconds", parsing_cycle_delay)
            time.sleep(parsing_cycle_delay)
