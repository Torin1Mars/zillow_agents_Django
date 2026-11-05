import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from zillow_agents_parser_app.models import Agent
from .data_cleaner import normalize_profile_url

logger = logging.getLogger(__name__)

def _decimal_or_none(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None

def _int_or_none(value):
    if value in (None, ""):
        return None
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return None

@transaction.atomic
def save_agent(general_card, extended_payload):
    extended = (extended_payload or {}).get("agent") or {}
    profile_url = normalize_profile_url(
        extended.get("profile_url") or general_card.get("url")
    )
    if not profile_url:
        raise ValueError("Agent has no valid profile URL")

    values = {
        "name": extended.get("name") or general_card.get("name") or "",
        "brokerage": general_card.get("brokerage") or "",
        "rating": _decimal_or_none(general_card.get("rating")),
        "reviews": _int_or_none(general_card.get("reviews")),
        "top_agent": bool(general_card.get("top_agent", False)),
        "team": bool(general_card.get("team", False)),
        "sales_12m": _int_or_none(general_card.get("sales_12m")) or 0,
        "email": extended.get("email") or None,
        "phone": extended.get("phone") or None,
        "broker_phone": extended.get("broker_phone") or None,
        "business_phone": extended.get("business_phone") or None,
        "company": extended.get("company") or None,
        "address": extended.get("address") or None,
        "city": extended.get("city") or None,
        "state": extended.get("state") or None,
        "zipcode": extended.get("zipcode") or None,
        "profile_photo": extended.get("profile_photo") or None,
        "screen_name": extended.get("screen_name") or None,
        "experience_years": str(extended.get("experience_years")) if extended.get("experience_years") is not None else None,
        "sales_history": (extended_payload or {}).get("sales_history") or [],
    }

    # URL is the stable fallback key; a provider ID can be added when available.
    agent, created = Agent.objects.update_or_create(profile_url=profile_url, defaults=values)
    logger.info("%s agent record: %s (%s)", "Created" if created else "Updated", agent.name, profile_url)
    return agent, created
