import imaplib
import logging

from django.conf import settings

from .base import EmailTransport, MessageParseError


# By default, imaplib will raise an exception if it encounters more
# than 10k bytes; sometimes users attempt to consume mailboxes that
# have a more, and modern computers are skookum-enough to handle just
# a *few* more messages without causing any sort of problem.
imaplib._MAXLINE = 1000000


logger = logging.getLogger(__name__)


class ImapTransport(EmailTransport):
    def __init__(
        self, hostname, port=None, ssl=False, tls=False,
        archive='', folder=None,
    ):
        self.max_message_size = getattr(
            settings,
            'DJANGO_MAILBOX_MAX_MESSAGE_SIZE',
            False
        )
        self.integration_testing_subject = getattr(
            settings,
            'DJANGO_MAILBOX_INTEGRATION_TESTING_SUBJECT',
            None
        )
        self.hostname = hostname
        self.port = port
        self.archive = archive
        self.folder = folder
        self.tls = tls
        if ssl:
            self.transport = imaplib.IMAP4_SSL
            if not self.port:
                self.port = 993
        else:
            self.transport = imaplib.IMAP4
            if not self.port:
                self.port = 143

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
        if self.tls:
            self.server.starttls()
        typ, msg = self.server.login(username, password)

        if self.folder:
            self.server.select(self.folder)
        else:
            self.server.select()

    def _get_all_message_ids(self):
        # Fetch all the message uids
        response, message_ids = self.server.uid('search', None, 'ALL')
        message_id_string = message_ids[0].strip()
        # Usually `message_id_string` will be a list of space-separated
        # ids; we must make sure that it isn't an empty string before
        # splitting into individual UIDs.
        if message_id_string:
            return message_id_string.decode().split(' ')
        return []

    def _get_small_message_ids(self, message_ids):
        # Using existing message uids, get the sizes and
        # return only those that are under the size
        # limit
        safe_message_ids = []

        status, data = self.server.uid(
            'fetch',
            ','.join(message_ids),
            '(RFC822.SIZE)'
        )

        for each_msg in data:
            each_msg = each_msg.decode()
            try:
                uid = each_msg.split(' ')[2]
                size = each_msg.split(' ')[4].rstrip(')')
                if int(size) <= int(self.max_message_size):
                    safe_message_ids.append(uid)
            except ValueError as e:
                logger.warning(
                    "ValueError: %s working on %s" % (e, each_msg[0])
                )
                pass
        return safe_message_ids

    def get_message(self, condition=None):
        message_ids = self._get_all_message_ids()

        if not message_ids:
            return

        # Limit the uids to the small ones if we care about that
        if self.max_message_size:
            message_ids = self._get_small_message_ids(message_ids)

        if self.archive:
            typ, folders = self.server.list(pattern=self.archive)
            if folders[0] is None:
                # If the archive folder does not exist, create it
                self.server.create(self.archive)

        for uid in message_ids:
            try:
                typ, msg_contents = self.server.uid('fetch', uid, '(RFC822)')
                if not msg_contents:
                    continue
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                except TypeError:
                    # This happens if another thread/process deletes the
                    # message between our generating the ID list and our
                    # processing it here.
                    continue

                if condition and not condition(message):
                    continue

                yield message
            except MessageParseError:
                continue

            if self.archive:
                self.server.uid('copy', uid, self.archive)

            self.server.uid('store', uid, "+FLAGS", "(\\Deleted)")
        self.server.expunge()
        return
