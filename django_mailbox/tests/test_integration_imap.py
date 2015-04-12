import os
import uuid

from six.moves.urllib import parse

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django_mailbox.models import Mailbox
from django_mailbox.tests.base import EmailMessageTestCase


__all__ = ['TestImap']


class TestImap(EmailMessageTestCase):
    def setUp(self):
        super(TestImap, self).setUp()
        self.test_imap_server = (
            os.environ['EMAIL_IMAP_SERVER']
        )
        self.mailbox = Mailbox.objects.create(
            name='Integration Test Imap',
            uri=self.get_connection_string()
        )
        self.arbitrary_identifier = str(uuid.uuid4())
        settings.DJANGO_MAILBOX_INTEGRATION_TESTING_SUBJECT = (
            self.arbitrary_identifier
        )

    def tearDown(self):
        settings.DJANGO_MAILBOX_INTEGRATION_TESTING_SUBJECT = None

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

        messages = self._get_new_messages(self.mailbox)

        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0].subject, self.arbitrary_identifier)
        self.assertEqual(messages[0].text, text_content)
