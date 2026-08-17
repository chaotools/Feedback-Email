import email
import unittest
from unittest.mock import patch

import feedback_api


class FakeSmtp:
    def login(self, *_args):
        pass

    def sendmail(self, *_args):
        self.message = _args[2]

    def quit(self):
        pass


class EmailEscapingTests(unittest.TestCase):
    @patch('feedback_api.smtplib.SMTP_SSL')
    def test_user_content_is_html_escaped(self, smtp_ssl):
        client = FakeSmtp()
        smtp_ssl.return_value = client

        feedback_api.send_email(
            '<img src=x onerror=alert(1)>',
            'user@example.com',
            'other',
            '💬 Other',
            '<script>alert(1)</script>'
        )

        message = email.message_from_string(client.message)
        html = message.get_payload()[1].get_payload(decode=True).decode('utf-8')
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertNotIn('<script>', html)


if __name__ == '__main__':
    unittest.main()
