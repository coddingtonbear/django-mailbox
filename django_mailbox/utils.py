import email.header
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


DEFAULT_CHARSET = getattr(
    settings,
    'DJANGO_MAILBOX_DEFAULT_CHARSET',
    'ascii',
)


def decode_header(header):
    try:
        return ''.join(
            [
                unicode(t[0], t[1] or DEFAULT_CHARSET)
                for t in email.header.decode_header(header)
            ]
        )
    except UnicodeDecodeError:
        logger.exception(
            'Errors encountered decoding header %s into encoding %s.',
            header,
            DEFAULT_CHARSET,
        )
        return unicode(header, DEFAULT_CHARSET, 'replace')
