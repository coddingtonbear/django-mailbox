import email
import os.path

from django.test import TestCase

from django_mailbox import models
from django_mailbox.models import Mailbox, Message


class EmailMessageTestCase(TestCase):
    ALLOWED_EXTRA_HEADERS = [
        'MIME-Version',
        'Content-Transfer-Encoding',
    ]

    def setUp(self):
        self._ALLOWED_MIMETYPES = models.ALLOWED_MIMETYPES
        self._STRIP_UNALLOWED_MIMETYPES = models.STRIP_UNALLOWED_MIMETYPES
        self._TEXT_STORED_MIMETYPES = models.TEXT_STORED_MIMETYPES

        self.mailbox = Mailbox.objects.create()
        super(EmailMessageTestCase, self).setUp()

    def _get_email_object(self, name):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                'messages',
                name,
            ),
            'r'
        ) as f:
            return email.message_from_string(
                f.read()
            )

    def _headers_identical(self, left, right, header=None):
        """ Check if headers are (close enough to) identical.

         * This is particularly tricky because Python 2.6, Python 2.7 and
           Python 3 each handle header strings slightly differently.  This
           should mash away all of the differences, though.
         * This also has a small loophole in that when re-writing e-mail
           payload encodings, we re-build the Content-Type header, so if the
           header was originally unquoted, it will be quoted when rehydrating
           the e-mail message.

        """
        if header.lower() == 'content-type':
            # Special case; given that we re-write the header, we'll be quoting
            # the new content type; we need to make sure that doesn't cause
            # this comparison to fail.  Also, the case of the encoding could
            # be changed, etc. etc. etc.
            left = left.replace('"', '').upper()
            right = right.replace('"', '').upper()
        left = left.replace('\n\t', ' ').replace('\n ', ' ')
        right = right.replace('\n\t', ' ').replace('\n ', ' ')
        if right != left:
            return False
        return True

    def compare_email_objects(self, left, right):
        # Compare headers
        for key, value in left.items():
            if not right[key] and key in self.ALLOWED_EXTRA_HEADERS:
                continue
            if not right[key]:
                raise AssertionError("Extra header '%s'" % key)
            if not self._headers_identical(right[key], value, header=key):
                raise AssertionError(
                    "Header '%s' unequal:\n%s\n%s" % (
                        key,
                        repr(value),
                        repr(right[key]),
                    )
                )
        for key, value in right.items():
            if not left[key] and key in self.ALLOWED_EXTRA_HEADERS:
                continue
            if not left[key]:
                raise AssertionError("Extra header '%s'" % key)
            if not self._headers_identical(left[key], value, header=key):
                raise AssertionError(
                    "Header '%s' unequal:\n%s\n%s" % (
                        key,
                        repr(value),
                        repr(right[key]),
                    )
                )
        if left.is_multipart() != right.is_multipart():
            self._raise_mismatched(left, right)
        if left.is_multipart():
            left_payloads = left.get_payload()
            right_payloads = right.get_payload()
            if len(left_payloads) != len(right_payloads):
                self._raise_mismatched(left, right)
            for n in range(len(left_payloads)):
                self.compare_email_objects(
                    left_payloads[n],
                    right_payloads[n]
                )
        else:
            if left.get_payload() is None or right.get_payload() is None:
                if left.get_payload() is None:
                    if right.get_payload is not None:
                        self._raise_mismatched(left, right)
                if right.get_payload() is None:
                    if left.get_payload is not None:
                        self._raise_mismatched(left, right)
            elif left.get_payload().strip() != right.get_payload().strip():
                self._raise_mismatched(left, right)

    def _raise_mismatched(self, left, right):
        raise AssertionError(
            "Message payloads do not match:\n%s\n%s" % (
                left.as_string(),
                right.as_string()
            )
        )

    def assertEqual(self, left, right):
        if not isinstance(left, email.message.Message):
            return super(EmailMessageTestCase, self).assertEqual(left, right)
        return self.compare_email_objects(left, right)

    def tearDown(self):
        for message in Message.objects.all():
            message.delete()
        models.ALLOWED_MIMETYPES = self._ALLOWED_MIMETYPES
        models.STRIP_UNALLOWED_MIMETYPES = self._STRIP_UNALLOWED_MIMETYPES
        models.TEXT_STORED_MIMETYPES = self._TEXT_STORED_MIMETYPES

        self.mailbox.delete()
        super(EmailMessageTestCase, self).tearDown()
