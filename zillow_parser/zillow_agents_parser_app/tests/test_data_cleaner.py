from django.test import SimpleTestCase
from zillow_agents_parser_app.services.data_cleaner import normalize_profile_url

class NormalizeProfileUrlTests(SimpleTestCase):
    def test_removes_query_and_trailing_slash(self):
        self.assertEqual(
            normalize_profile_url("https://www.example.com/profile/name/?a=1"),
            "https://www.example.com/profile/name",
        )

    def test_empty_url(self):
        self.assertIsNone(normalize_profile_url(""))
