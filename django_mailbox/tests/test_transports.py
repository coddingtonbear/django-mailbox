import mock
import six

from django_mailbox.tests.base import EmailMessageTestCase
from django_mailbox.transports import ImapTransport, Pop3Transport


class TestImapTransport(EmailMessageTestCase):
    def setUp(self):
        self.arbitrary_hostname = 'one.two.three'
        self.arbitrary_port = 100
        self.ssl = False
        self.transport = ImapTransport(
            self.arbitrary_hostname,
            self.arbitrary_port,
            self.ssl
        )
        self.transport.server = None
        super(TestImapTransport, self).setUp()

    def test_get_email_message(self):
        with mock.patch.object(self.transport, 'server') as server:
            server.search.return_value = (
                'OK',
                [
                    'One',  # This is totally arbitrary
                ]
            )
            server.fetch.return_value = (
                'OK',
                [
                    [
                        '1 (RFC822 {8190}',  # Wat?
                        self._get_email_as_text('generic_message.eml')
                    ],
                    ')',
                ]
            )

            actual_messages = list(self.transport.get_message())

        self.assertEqual(len(actual_messages), 1)

        actual_message = actual_messages[0]
        expected_message = self._get_email_object('generic_message.eml')

        self.assertEqual(expected_message, actual_message)



class TestPop3Transport(EmailMessageTestCase):
    def setUp(self):
        self.arbitrary_hostname = 'one.two.three'
        self.arbitrary_port = 100
        self.ssl = False
        self.transport = Pop3Transport(
            self.arbitrary_hostname,
            self.arbitrary_port,
            self.ssl
        )
        self.transport.server = None
        super(TestPop3Transport, self).setUp()

    def test_get_email_message(self):
        with mock.patch.object(self.transport, 'server') as server:
            # Consider this value arbitrary, the second parameter
            # should have one entry per message in the inbox
            server.list.return_value = [None, ['some_msg']]
            server.retr.return_value = [
                '+OK message follows',
                [
                    line.encode('ascii')
                    for line in self._get_email_as_text(
                        'generic_message.eml'
                    ).decode('ascii').split('\n')
                ],
                10018,  # Some arbitrary size, ideally matching the above
            ]

            actual_messages = list(self.transport.get_message())

        self.assertEqual(len(actual_messages), 1)

        actual_message = actual_messages[0]
        expected_message = self._get_email_object('generic_message.eml')

        self.assertEqual(expected_message, actual_message)
