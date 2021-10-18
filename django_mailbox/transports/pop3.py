from poplib import POP3, POP3_SSL

from .base import EmailTransport, MessageParseError


class Pop3Transport(EmailTransport):
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

    def get_message_body(self, message_lines):
        return bytes('\r\n', 'ascii').join(message_lines)

    def get_message(self, condition=None):
        message_count = len(self.server.list()[1])
        for i in range(message_count):
            try:
                msg_contents = self.get_message_body(
                    self.server.retr(i + 1)[1]
                )
                message = self.get_email_from_bytes(msg_contents)

                if condition and not condition(message):
                    continue

                yield message
            except MessageParseError:
                continue
            self.server.dele(i + 1)
        self.server.quit()
        return
