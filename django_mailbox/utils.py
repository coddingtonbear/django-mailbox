import email.header
import logging

import six

from django.conf import settings


logger = logging.getLogger(__name__)


DEFAULT_CHARSET = getattr(
    settings,
    'DJANGO_MAILBOX_DEFAULT_CHARSET',
    'iso8859-1',
)


def convert_header_to_unicode(header):
    def _decode(value, encoding):
        if isinstance(value, six.text_type):
            return value
        if not encoding or encoding == 'unknown-8bit':
            encoding = DEFAULT_CHARSET
        return value.decode(encoding, 'REPLACE')

    try:
        return ''.join(
            [
                (
                    _decode(bytestr, encoding)
                ) for bytestr, encoding in email.header.decode_header(header)
            ]
        )
    except UnicodeDecodeError:
        logger.exception(
            'Errors encountered decoding header %s into encoding %s.',
            header,
            DEFAULT_CHARSET,
        )
        return unicode(header, DEFAULT_CHARSET, 'replace')


def get_body_from_message(message, maintype, subtype):
    """
    Fetchs the body message matching main/sub content type.
    """
    body = six.text_type('')
    for part in message.walk():
        if part.get_content_maintype() == maintype and \
                part.get_content_subtype() == subtype:
            charset = part.get_content_charset()
            this_part = part.get_payload(decode=True)
            if charset:
                this_part = this_part.decode(charset, 'replace')

            try:
                body += this_part
            except ValueError:
                # Since it did not declare a charset, and we
                # *should* be 7-bit clean right now, let's assume it
                # is ASCII.
                body += this_part.decode('ascii', 'replace')
                logger.warning(
                    'Error encountered while decoding text '
                    'payload from an incorrectly-constructed '
                    'e-mail; payload was converted to ASCII with '
                    'replacement, but some data may not be '
                    'represented as the sender intended.'
                )

    return body
