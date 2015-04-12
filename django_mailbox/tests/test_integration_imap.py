import os
import urllib
import uuid

from django.core.mail import EmailMultiAlternatives

from django_mailbox.models import Mailbox
from django_mailbox.tests.base import EmailMessageTestCase


class TestImap(EmailMessageTestCase):
    def setUp(self):
        self.test_imap_server = (
            os.environ['EMAIL_IMAP_SERVER']
        )
        self.mailbox = Mailbox.objects.create(
            name='Integration Test Imap',
            uri=self.get_connection_string()
        )

    def get_connection_string(self):
        return "imap+ssl://{account}:{password}@{server}".format(
            account=urllib.quote(self.test_account),
            password=urllib.quote(self.test_password),
            server=self.test_imap_server,
        )

    def test_get_imap_message(self):
        arbitrary_identifier = uuid.uuid4()
        text_content = 'This is some content'
        msg = EmailMultiAlternatives(
            arbitrary_identifier,
            text_content,
            self.test_from_email,
            [
                self.test_account,
            ]
        )
        msg.send()

        messages = self.get_new_messages()

        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0].subject, arbitrary_identifier)
        self.assertEqual(messages[0].text, text_content)
