import email

# Do *not* remove this, we need to use this in subclasses of EmailTransport
from email.errors import MessageParseError  # noqa: F401


class EmailTransport:
    def get_email_from_bytes(self, contents):
        message = email.message_from_bytes(contents)

        return message


class PluggableEmailTransport(EmailTransport):
    @classmethod
    def from_uri(cls, uri):
        raise NotImplemented("The class does not implement {0}.from_uri, and it should. "
                             "Overwrite {0}.from_uri.".format(cls.__name__))
