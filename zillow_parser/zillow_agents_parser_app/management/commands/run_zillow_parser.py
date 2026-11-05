import logging
from django.core.management.base import BaseCommand
from zillow_agents_parser_app.services.parsing_manager import ParsingManager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the two-stage Zillow agent parser using configured search locations."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Run one parsing cycle and exit.")
        parser.add_argument("--pause", type=int, default=300, help="Seconds between cycles (default: 300).")

    def handle(self, *args, **options):
        manager = ParsingManager()
        logger.info("Zillow Agents Parser started")
        if options["once"]:
            manager.run_once()
        else:
            manager.run_forever(max(30, options["pause"]))
