import unittest

from delivery.resend import parse_recipients


class DeliveryTests(unittest.TestCase):
    def test_parse_recipients_accepts_commas_and_semicolons(self) -> None:
        recipients = parse_recipients("a@example.com; b@example.com, c@example.com")
        self.assertEqual(recipients, ["a@example.com", "b@example.com", "c@example.com"])


if __name__ == "__main__":
    unittest.main()
