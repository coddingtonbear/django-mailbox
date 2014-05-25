from imaplib import IMAP4, IMAP4_SSL

from .base import EmailTransport, MessageParseError


class ImapTransport(EmailTransport):
    def __init__(self, hostname, port=None, ssl=False, archive=''):
        self.hostname = hostname
        self.port = port
        self.archive = archive
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

    def get_message(self):
        typ, inbox = self.server.search(None, 'ALL')

        if not inbox[0]:
            return

        if self.archive:
            typ, folders = self.server.list(pattern=self.archive)
            if folders[0] is None:
                # If the archive folder does not exist, create it
                self.server.create(self.archive)

        for key in inbox[0].split():
            try:
                typ, msg_contents = self.server.fetch(key, '(RFC822)')
                message = self.get_email_from_bytes(msg_contents[0][1])
                yield message
            except MessageParseError:
                continue

            if self.archive:
                self.server.copy(key, self.archive)

            self.server.store(key, "+FLAGS", "\\Deleted")
        self.server.expunge()
        return
