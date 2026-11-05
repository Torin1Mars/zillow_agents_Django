from urllib.parse import urlsplit, urlunsplit

def normalize_profile_url(url):
    if not url:
        return None
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        return None
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))

def clean_general_card(card):
    cleaned = dict(card)
    cleaned["url"] = normalize_profile_url(card.get("url"))
    cleaned["name"] = (card.get("name") or "").strip()
    cleaned["brokerage"] = (card.get("brokerage") or "").strip()
    return cleaned
