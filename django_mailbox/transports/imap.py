import email
from imaplib import IMAP4, IMAP4_SSL


class ImapTransport(object):
    def __init__(self, hostname, port=None, ssl=False):
        self.hostname = hostname
        self.port = port
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

        for key in inbox[0].split():
            try:
                typ, msg_contents = self.server.fetch(key, '(RFC822)')
                message = email.message_from_string(msg_contents[0][1])
                yield message
            except email.Errors.MessageParseError:
                continue
            self.server.store(key, "+FLAGS", "\\Deleted")
        self.server.expunge()
        return
