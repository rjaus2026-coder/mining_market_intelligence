import unittest

from delivery.resend import _request_headers, parse_recipients


class DeliveryTests(unittest.TestCase):
    def test_parse_recipients_accepts_commas_and_semicolons(self) -> None:
        recipients = parse_recipients("a@example.com; b@example.com, c@example.com")
        self.assertEqual(recipients, ["a@example.com", "b@example.com", "c@example.com"])

    def test_request_headers_include_user_agent(self) -> None:
        headers = _request_headers("test-key")
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        self.assertIn("User-Agent", headers)
        self.assertEqual(headers["Accept"], "application/json")


if __name__ == "__main__":
    unittest.main()
