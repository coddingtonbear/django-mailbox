from imaplib import IMAP4, IMAP4_SSL

from .base import EmailTransport, MessageParseError

from django.conf import settings

MAX_MESSAGE_SIZE = getattr(
    settings,
    'DJANGO_MAILBOX_MAX_MESSAGE_SIZE',
    False
)

class ImapTransport(EmailTransport):
    def __init__(self, hostname, port=None, ssl=False, archive=''):
        self.hostname = hostname
        self.port = port
        self.archive = archive
        self.MAX_MSG_SIZE = MAX_MESSAGE_SIZE
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
        self.server.select()


    def _get_all_message_ids(self):
        # Fetch all the message uids
        response, message_ids = self.server.uid('search', None, 'ALL', )
        return message_ids[0].split(' ')

    def _get_small_message_ids(self, message_ids):
        # Using existing message uids, get the sizes and
        # return only those that are under the size
        # limit
        safe_message_ids = []

        status, data = self.server.uid(
            'fetch',
            ','.join(message_ids),
            '(BODY.PEEK[HEADER] RFC822.SIZE BODYSTRUCTURE)'
        )

        for each_msg in data:
            if isinstance(each_msg, tuple):
                try:
                    metadata, structure = each_msg[0].split(' BODYSTRUCTURE ')
                    uid = metadata.split('(')[1].split(' ')[1]
                    size = metadata.split('(')[1].split(' ')[3]
                    if int(size) <= int(self.MAX_MSG_SIZE):
                        safe_message_ids.append(uid)
                except ValueError, e:
                    print "ValueError: %s working on %s" % (e, each_msg[0])
                    print each_msg
                    pass
        return safe_message_ids

    def get_message(self):
        message_ids = self._get_all_message_ids()

        # Limit the uids to the small ones if we care about that
        if self.MAX_MSG_SIZE:
            message_ids = self._get_small_message_ids(message_ids)


        if not message_ids:
            return

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

            self.server.uid('store', uid, "+FLAGS", "\\Deleted")
        self.server.expunge()
        return
