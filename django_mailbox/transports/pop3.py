import email
from poplib import POP3, POP3_SSL

class Pop3Transport(object):
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
