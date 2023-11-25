from unittest import mock

from django.test.utils import override_settings

from django_mailbox.tests.base import EmailMessageTestCase, get_email_as_text
from django_mailbox.transports import ImapTransport, Pop3Transport

FAKE_UID_SEARCH_ANSWER = (
    'OK',
    [
        b'18 19 20 21 22 23 24 25 26 27 28 29 ' +
        b'30 31 32 33 34 35 36 37 38 39 40 41 42 43 44'
    ]
)
FAKE_UID_FETCH_SIZES = (
    'OK',
    [
        b'1 (UID 18 RFC822.SIZE 58070000000)',
        b'2 (UID 19 RFC822.SIZE 2593)'
    ]
)
FAKE_UID_FETCH_MSG = (
    'OK',
    [
        (
            b'1 (UID 18 RFC822 {5807}',
            get_email_as_text('generic_message.eml')
        ),
    ]
)
FAKE_UID_COPY_MSG = (
    'OK',
    [
        b'[COPYUID 1 2 2] (Success)'
    ]
)
FAKE_LIST_ARCHIVE_FOLDERS_ANSWERS = (
    'OK',
    [
        b'(\\HasNoChildren \\All) "/" "[Gmail]/All Mail"'
    ]
)


class IMAPTestCase(EmailMessageTestCase):
    def setUp(self):
        def imap_server_uid_method(*args):
            cmd = args[0]
            arg2 = args[2]
            if cmd == 'search':
                return FAKE_UID_SEARCH_ANSWER
            if cmd == 'copy':
                return FAKE_UID_COPY_MSG
            if cmd == 'fetch':
                if arg2 == '(RFC822.SIZE)':
                    return FAKE_UID_FETCH_SIZES
                if arg2 == '(RFC822)':
                    return FAKE_UID_FETCH_MSG

        def imap_server_list_method(pattern=None):
            return FAKE_LIST_ARCHIVE_FOLDERS_ANSWERS

        self.imap_server = mock.Mock()
        self.imap_server.uid = imap_server_uid_method
        self.imap_server.list = imap_server_list_method
        super().setUp()


class TestImapTransport(IMAPTestCase):
    def setUp(self):
        super().setUp()
        self.arbitrary_hostname = 'one.two.three'
        self.arbitrary_port = 100
        self.ssl = False
        self.transport = ImapTransport(
            self.arbitrary_hostname,
            self.arbitrary_port,
            self.ssl
        )
        self.transport.server = self.imap_server

    def test_get_email_message(self):
        actual_messages = list(self.transport.get_message())
        self.assertEqual(len(actual_messages), 27)
        actual_message = actual_messages[0]
        expected_message = self._get_email_object('generic_message.eml')
        self.assertEqual(expected_message, actual_message)


class TestImapArchivedTransport(TestImapTransport):
    def setUp(self):
        super().setUp()
        self.archive = 'Archive'
        self.transport = ImapTransport(
            self.arbitrary_hostname,
            self.arbitrary_port,
            self.ssl,
            self.archive
        )
        self.transport.server = self.imap_server


class TestMaxSizeImapTransport(TestImapTransport):

    @override_settings(DJANGO_MAILBOX_MAX_MESSAGE_SIZE=5807)
    def setUp(self):
        super().setUp()

        self.transport = ImapTransport(
            self.arbitrary_hostname,
            self.arbitrary_port,
            self.ssl,
        )
        self.transport.server = self.imap_server

    def test_size_limit(self):
        all_message_ids = self.transport._get_all_message_ids()
        small_message_ids = self.transport._get_small_message_ids(
            all_message_ids,
        )
        self.assertEqual(len(small_message_ids), 1)

    def test_get_email_message(self):
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
        super().setUp()

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
