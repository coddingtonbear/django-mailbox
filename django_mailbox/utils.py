import email.header
import logging
from email import utils
from email import charset
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
        return value.decode(encoding, 'replace')

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
                try:
                    this_part = this_part.decode(charset, 'replace')
                except LookupError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Unknown encoding %s encountered while decoding '
                        'text payload.  Interpreting as ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.',
                        charset
                    )
                except ValueError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Error encountered while decoding text '
                        'payload from an incorrectly-constructed '
                        'e-mail; payload was converted to ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.'
                    )
            else:
                this_part = this_part.decode('ascii', 'replace')

            body += this_part

    return body

# From http://tools.ietf.org/html/rfc5322#section-3.6
ADDR_HEADERS = ('resent-from',
                'resent-sender',
                'resent-to',
                'resent-cc',
                'resent-bcc',
                'from',
                'sender',
                'reply-to',
                'to',
                'cc',
                'bcc')

PARAM_HEADERS = ('content-type',
                 'content-disposition')


def cleanup_message(message, addr_headers=None, param_headers=None):
    """
    Cleanup a `Message` handling header and payload charsets.

    Headers are handled in the most sane way possible.  Address names
    are left in `ascii` if possible or encoded to `latin_1` or `utf-8`
    and finally encoded according to RFC 2047 without encoding the
    address, something the `email` stdlib package doesn't do.
    Parameterized headers such as `filename` in the
    `Content-Disposition` header, have their values encoded properly
    while leaving the rest of the header to be handled without
    encoding.  Finally, all other header are left in `ascii` if
    possible or encoded to `latin_1` or `utf-8` as a whole.

    The message is modified in place and is also returned in such a
    state that it can be safely encoded to ascii.
    """

    if addr_headers is None:
        addr_headers = ADDR_HEADERS
    if param_headers is None:
        param_headers = PARAM_HEADERS

    for key, value in message.items():
        if key.lower() in addr_headers:
            addrs = []
            for name, addr in utils.getaddresses([value]):
                best, encoded = best_charset(name)
                if six.PY2:
                    name = encoded
                name = charset.Charset(best).header_encode(name)
                addrs.append(utils.formataddr((name, addr)))
            value = ', '.join(addrs)
            message.replace_header(key, value)
        if key.lower() in param_headers:
            for param_key, param_value in message.get_params(header=key):
                if param_value:
                    best, encoded = best_charset(param_value)
                    if six.PY2:
                        param_value = encoded
                    if best == 'ascii':
                        best = None
                    message.set_param(param_key, param_value,
                                      header=key, charset=best)
        else:
            best, encoded = best_charset(value)
            if six.PY2:
                value = encoded
            value = charset.Charset(best).header_encode(value)
            message.replace_header(key, value)

    payload = message.get_payload()
    if payload and isinstance(payload, six.text_type):
        best, encoded = best_charset(payload)
        if six.PY2:
            payload = encoded
        message.set_payload(payload, charset=best)
    elif isinstance(payload, list):
        for part in payload:
            cleanup_message(part)

    return message


def encode_message(message,
                   addr_headers=ADDR_HEADERS, param_headers=PARAM_HEADERS):
    """
    Encode a `Message` handling headers and payloads.

    Headers are handled in the most sane way possible.  Address names
    are left in `ascii` if possible or encoded to `latin_1` or `utf-8`
    and finally encoded according to RFC 2047 without encoding the
    address, something the `email` stdlib package doesn't do.
    Parameterized headers such as `filename` in the
    `Content-Disposition` header, have their values encoded properly
    while leaving the rest of the header to be handled without
    encoding.  Finally, all other header are left in `ascii` if
    possible or encoded to `latin_1` or `utf-8` as a whole.

    The return is a byte string of the whole message.
    """
    cleanup_message(message)
    return message.as_string().encode('ascii')


def best_charset(text):
    """
    Find the most human-readable and/or conventional encoding for unicode text.

    Prefers `ascii` or `latin_1` and falls back to `utf_8`.
    """
    encoded = text
    for charset in 'ascii', 'latin_1', 'utf_8':
        try:
            encoded = text.encode(charset)
        except UnicodeError:
            pass
        else:
            return charset, encoded
