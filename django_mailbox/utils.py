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
