from imaplib import IMAP4, IMAP4_SSL
import logging

from django.conf import settings

from .base import EmailTransport, MessageParseError


logger = logging.getLogger(__name__)


class ImapTransport(EmailTransport):
    def __init__(self, hostname, port=None, ssl=False, archive='', folder=None):
        self.max_message_size = getattr(
            settings,
            'DJANGO_MAILBOX_MAX_MESSAGE_SIZE',
            False
        )
        self.hostname = hostname
        self.port = port
        self.archive = archive
        self.folder = folder
        if ssl:
            self.transport = IMAP4_SSL
            if not self.port:
                self.port = 993
        else:
            self.transport = IMAP4
            if not self.port:
                self.port = 143

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
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
            return message_id_string.split(' ')
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

    def get_message(self):
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
                message = self.get_email_from_bytes(msg_contents[0][1])
                yield message
            except MessageParseError:
                continue

            if self.archive:
                self.server.uid('copy', uid, self.archive)

            self.server.uid('store', uid, "+FLAGS", "(\\Deleted)")
        self.server.expunge()
        return
