import os
import uuid

from six.moves.urllib import parse

from django.core.mail import EmailMultiAlternatives

from django_mailbox.models import Mailbox
from django_mailbox.tests.base import EmailMessageTestCase


__all__ = ['TestImap']


class TestImap(EmailMessageTestCase):
    def setUp(self):
        super(TestImap, self).setUp()

        self.test_imap_server = (
            os.environ.get('EMAIL_IMAP_SERVER')
        )

        required_settings = [
            self.test_imap_server,
            self.test_account,
            self.test_password,
            self.test_smtp_server,
            self.test_from_email,
        ]
        if not all(required_settings):
            self.skipTest(
                "Integration tests are not available without having "
                "the the following environment variables set: "
                "EMAIL_ACCOUNT, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, "
                "EMAIL_IMAP_SERVER."
            )

        self.mailbox = Mailbox.objects.create(
            name='Integration Test Imap',
            uri=self.get_connection_string()
        )
        self.arbitrary_identifier = str(uuid.uuid4())

    def get_connection_string(self):
        return "imap+ssl://{account}:{password}@{server}".format(
            account=parse.quote(self.test_account),
            password=parse.quote(self.test_password),
            server=self.test_imap_server,
        )

    def test_get_imap_message(self):
        text_content = 'This is some content'
        msg = EmailMultiAlternatives(
            self.arbitrary_identifier,
            text_content,
            self.test_from_email,
            [
                self.test_account,
            ]
        )
        msg.send()

        messages = self._get_new_messages(
            self.mailbox,
            condition=lambda m: m['subject'] == self.arbitrary_identifier
        )

        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0].subject, self.arbitrary_identifier)
        self.assertEqual(messages[0].text, text_content)
