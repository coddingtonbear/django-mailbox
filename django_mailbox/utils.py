import email.header
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


DEFAULT_CHARSET = getattr(
    settings,
    'DJANGO_MAILBOX_DEFAULT_CHARSET',
    'iso8859-1',
)


def convert_header_to_unicode(header):
    try:
        return ''.join(
            [
                (
                    bytestr.decode(encoding, 'REPLACE')
                    if encoding
                    else bytestr.decode(DEFAULT_CHARSET, 'REPLACE')
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
