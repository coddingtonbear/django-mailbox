import email
from imaplib import IMAP4
from poplib import POP3

class PopMailEnumerator(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def connect(self, username, password):
        self.server = POP3(self.hostname, self.port)
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
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def connect(self, username, password):
        self.server = IMAP4(self.hostname, self.port)
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

