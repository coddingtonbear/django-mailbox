import email

import six

# Do *not* remove this, we need to use this in subclasses of EmailTransport
if six.PY3:
    from email.errors import MessageParseError  # noqa: F401
else:
    from email.Errors import MessageParseError  # noqa: F401


class EmailTransport(object):
    def get_email_from_bytes(self, contents):
        if six.PY3:
            message = email.message_from_bytes(contents)
        else:
            message = email.message_from_string(contents)

        return message


class PluggableEmailTransport(EmailTransport):
    @classmethod
    def from_uri(cls, uri):
        raise NotImplemented("The class does not implement {0}.from_uri, and it should. "
                             "Overwrite {0}.from_uri.".format(cls.__name__))
