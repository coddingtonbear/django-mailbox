import email
import os.path

from django.test import TestCase
import six

from django_mailbox import models
from django_mailbox.models import Mailbox, Message


class TestMailbox(TestCase):
    def test_protocol_info(self):
        mailbox = Mailbox()
        mailbox.uri = 'alpha://test.com'

        expected_protocol = 'alpha'
        actual_protocol = mailbox._protocol_info.scheme

        self.assertEqual(
            expected_protocol,
            actual_protocol,
        )


class EmailMessageTestCase(TestCase):
    def setUp(self):
        self._ALLOWED_MIMETYPES = models.ALLOWED_MIMETYPES
        self._STRIP_UNALLOWED_MIMETYPES = models.STRIP_UNALLOWED_MIMETYPES
        self._TEXT_STORED_MIMETYPES = models.TEXT_STORED_MIMETYPES

        self.mailbox = Mailbox.objects.create()
        super(EmailMessageTestCase, self).setUp()

    def _get_email_object(self, name):
        with open(os.path.join(os.path.dirname(__file__), name), 'r') as f:
            return email.message_from_string(
                f.read()
            )

    def _headers_identical(self, left, right):
        """ Check if headers are identical.

        This is particularly tricky because Python 2.6, Python 2.7 and Python 3
        each handle this slightly differently.  This should mash away all
        of the differences, though.

        """
        left = left.replace('\n\t', ' ').replace('\n ', ' ')
        right = right.replace('\n\t', ' ').replace('\n ', ' ')
        if right != left:
            return False
        return True

    def compare_email_objects(self, left, right):
        # Compare headers
        for key, value in left.items():
            if not right[key]:
                raise AssertionError("Extra header '%s'" % key)
            if not self._headers_identical(right[key], value):
                raise AssertionError(
                    "Header '%s' unequal:\n%s\n%s" % (
                        key,
                        repr(value),
                        repr(right[key]),
                    )
                )
        for key, value in right.items():
            if not left[key]:
                raise AssertionError("Extra header '%s'" % key)
            if not self._headers_identical(left[key], value):
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


class TestProcessEmail(EmailMessageTestCase):
    def test_message_without_attachments(self):
        message = self._get_email_object('generic_message.eml')

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        self.assertEqual(
            msg.mailbox,
            mailbox
        )
        self.assertEqual(msg.subject, 'Message Without Attachment')
        self.assertEqual(
            msg.message_id,
            (
                '<CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z'
                '-foqTO60zA@mail.gmail.com>'
            )
        )
        self.assertEqual(
            msg.from_header,
            'Adam Coddington <test@adamcoddington.net>',
        )
        self.assertEqual(
            msg.to_header,
            'Adam Coddington <test@adamcoddington.net>',
        )

    def test_message_with_attachments(self):
        message = self._get_email_object('message_with_attachment.eml')

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        expected_count = 1
        actual_count = msg.attachments.count()

        self.assertEqual(
            expected_count,
            actual_count,
        )

        attachment = msg.attachments.all()[0]
        self.assertEqual(
            attachment.get_filename(),
            'heart.png',
        )

    def test_message_get_text_body(self):
        message = self._get_email_object('multipart_text.eml')

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        expected_results = 'Hello there!'
        actual_results = msg.get_text_body().strip()

        self.assertEqual(
            expected_results,
            actual_results,
        )


class TestGetMessage(EmailMessageTestCase):
    def test_get_text_body_properly_recomposes_line_continuations(self):
        message = Message()
        email_object = self._get_email_object(
            'message_with_long_text_lines.eml'
        )

        message.get_email_object = lambda: email_object

        actual_text = message.get_text_body()
        expected_text = (
            'The one of us with a bike pump is far ahead, '
            'but a man stopped to help us and gave us his pump.'
        )

        self.assertEqual(
            actual_text,
            expected_text
        )


class TestMessageFlattening(EmailMessageTestCase):
    def test_quopri_message_is_properly_rehydrated(self):
        incoming_email_object = self._get_email_object(
            'message_with_many_multiparts.eml',
        )
        # Note: this is identical to the above, but it appears that
        # while reading-in an e-mail message, we do alter it slightly
        expected_email_object = self._get_email_object(
            'message_with_many_multiparts.eml',
        )
        models.TEXT_STORED_MIMETYPES = ['text/plain']

        msg = self.mailbox.process_incoming_message(incoming_email_object)

        actual_email_object = msg.get_email_object()

        self.assertEqual(
            actual_email_object,
            expected_email_object,
        )

    def test_base64_message_is_properly_rehydrated(self):
        incoming_email_object = self._get_email_object(
            'message_with_attachment.eml',
        )
        # Note: this is identical to the above, but it appears that
        # while reading-in an e-mail message, we do alter it slightly
        expected_email_object = self._get_email_object(
            'message_with_attachment.eml',
        )

        msg = self.mailbox.process_incoming_message(incoming_email_object)

        actual_email_object = msg.get_email_object()

        self.assertEqual(
            actual_email_object,
            expected_email_object,
        )

    def test_message_handles_rehydration_problems(self):
        incoming_email_object = self._get_email_object(
            'message_with_defective_attachment_association.eml',
        )
        expected_email_object = self._get_email_object(
            'message_with_defective_attachment_association_result.eml',
        )
        # Note: this is identical to the above, but it appears that
        # while reading-in an e-mail message, we do alter it slightly
        message = Message()
        message.body = incoming_email_object.as_string()

        msg = self.mailbox.process_incoming_message(incoming_email_object)

        actual_email_object = msg.get_email_object()

        self.assertEqual(
            actual_email_object,
            expected_email_object,
        )

    def test_message_content_type_stripping(self):
        incoming_email_object = self._get_email_object(
            'message_with_many_multiparts.eml',
        )
        expected_email_object = self._get_email_object(
            'message_with_many_multiparts_stripped_html.eml',
        )
        models.STRIP_UNALLOWED_MIMETYPES = True
        models.ALLOWED_MIMETYPES = ['text/plain']

        msg = self.mailbox.process_incoming_message(incoming_email_object)

        actual_email_object = msg.get_email_object()

        self.assertEqual(
            actual_email_object,
            expected_email_object,
        )


class TestMessageGetEmailObject(TestCase):
    def test_get_body_properly_handles_unicode_body(self):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                'generic_message.eml'
            )
        ) as f:
            unicode_body = six.u(f.read())

        message = Message()
        message.body = unicode_body

        expected_body = unicode_body
        actual_body = message.get_email_object().as_string()

        self.assertEqual(
            expected_body,
            actual_body
        )
