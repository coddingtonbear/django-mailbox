import email
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL

class PopMailEnumerator(object):
    def __init__(self, hostname, port=None, ssl=False):
        self.hostname = hostname
        self.port = port
        if ssl:
            self.transport = POP3_SSL
            if not self.port:
                self.port = 995
        else:
            self.transport = POP3
            if not self.port:
                self.port = 110

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
        self.server.user(username)
        self.server.pass_(password)

    def get_message(self):
        message_count = len(self.server.list()[1])
        for i in range(message_count):
            try:
                msg_contents = "\r\n".join(self.server.retr(i + 1)[1])
                message = email.message_from_string(msg_contents)
                yield message
            except email.Errors.MessageParseError:
                continue
            self.server.dele(i + 1)
        self.server.quit()
        return

class ImapMailEnumerator(object):
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
        for key in inbox[0].split():
            try:
                typ, msg_contents = self.server.fetch(key, '(RFC822)')
                message = email.message_from_string(msg_contents[0][1])
                yield message
            except email.Errors.MessageParseError:
                continue
            self.server.store(key, "+FLAGS", "\\Deleted");
        self.server.expunge()
        return

