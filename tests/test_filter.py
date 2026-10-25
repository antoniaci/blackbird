import unittest

from src.modules.utils.filter import filterAccounts, parseFilter


class TestFilter(unittest.TestCase):
    site = {"name": "Mastodon", "cat": "social", "e_code": 200}

    def test_combined_conditions(self):
        self.assertTrue(filterAccounts("name~Mastodon and cat=social", self.site))
        self.assertTrue(filterAccounts("e_code>=200 OR name=unknown", self.site))
        self.assertFalse(filterAccounts("name=unknown and cat=social", self.site))

    def test_malformed_expressions_are_rejected(self):
        for expression in (
            "name=Mastodon cat=social",
            "name==Mastodon",
            "name=Mastodon and",
        ):
            with self.subTest(expression=expression):
                self.assertEqual(parseFilter(expression), ([], []))
                self.assertFalse(filterAccounts(expression, self.site))

    def test_non_numeric_comparison_does_not_raise(self):
        self.assertFalse(filterAccounts("name>not-a-number", self.site))


if __name__ == "__main__":
    unittest.main()
