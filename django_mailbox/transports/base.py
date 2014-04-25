import email

import six

# Do *not* remove this, we need to use this in subclasses of EmailTransport
if six.PY3:
    from email.errors import MessageParseError
else:
    from email.Errors import MessageParseError


class EmailTransport(object):
    def get_email_from_bytes(self, contents):
        if six.PY3:
            message = email.message_from_bytes(contents)
        else:
            message = email.message_from_string(contents)

        return message
