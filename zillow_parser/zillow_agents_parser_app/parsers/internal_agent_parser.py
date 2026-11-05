import json
import logging
import random
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class InternalAgentParser:
    """Extracts extended profile information and sales history."""

    def __init__(self, fetcher, delay_range=(1, 6)):
        self.fetcher = fetcher
        self.delay_range = delay_range

    def parse_profile(self, profile_url):
        html = self.fetcher.fetch_html(profile_url)
        time.sleep(random.randint(*self.delay_range))
        soup = BeautifulSoup(html, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data is None:
            raise RuntimeError("__NEXT_DATA__ not found in compatible profile response")
        data = json.loads(next_data.string or next_data.get_text())
        page_data = data["props"]["pageProps"]
        return {
            "agent": self.parse_extended_agent_data(page_data),
            "sales_history": self.parse_agent_sales(page_data),
        }

    @staticmethod
    def parse_extended_agent_data(page_data):
        agent = page_data.get("displayUser") or {}
        business_address = agent.get("businessAddress") or {}
        phone_numbers = agent.get("phoneNumbers") or {}
        know_me = agent.get("getToKnowMe") or {}
        return {
            "name": agent.get("name"),
            "email": agent.get("email"),
            "phone": phone_numbers.get("cell"),
            "broker_phone": phone_numbers.get("brokerage"),
            "business_phone": phone_numbers.get("business"),
            "company": agent.get("businessName"),
            "address": business_address.get("address1"),
            "city": business_address.get("city"),
            "state": business_address.get("state"),
            "zipcode": business_address.get("postalCode"),
            "profile_url": page_data.get("currentUrl"),
            "profile_photo": agent.get("profilePhotoSrc"),
            "screen_name": agent.get("screenName"),
            "experience_years": know_me.get("yearsInIndustry"),
        }

    @staticmethod
    def parse_agent_sales(page_data):
        sales = page_data.get("pastSales", {}).get("past_sales", []) or []
        return [{
            "address": sale.get("street_address"),
            "city": sale.get("city"),
            "state": sale.get("state"),
            "zipcode": sale.get("city_state_zipcode"),
            "price": sale.get("price"),
            "sold_date": sale.get("sold_date"),
            "represented": sale.get("represented"),
            "bedrooms": sale.get("bedrooms"),
            "bathrooms": sale.get("bathrooms"),
            "living_area": sale.get("livingAreaValue"),
            "image": sale.get("image_url"),
            "property_url": sale.get("home_details_url"),
        } for sale in sales]
