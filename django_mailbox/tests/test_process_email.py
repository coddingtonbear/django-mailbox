import os.path

import six

from django_mailbox.models import Mailbox, Message
from django_mailbox.tests.base import EmailMessageTestCase


__all__ = ['TestProcessEmail']


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

    def test_get_body_properly_handles_unicode_body(self):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                'messages/generic_message.eml'
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

    def test_message_with_misplaced_utf8_content(self):
        """ Ensure that we properly handle incorrectly encoded messages

        ``message_with_utf8_char.eml``'s primary text payload is marked
        as being iso-8859-1 data, but actually contains UTF-8 bytes.

        """
        email_object = self._get_email_object('message_with_utf8_char.eml')

        msg = self.mailbox.process_incoming_message(email_object)

        actual_text = msg.get_text_body()
        expected_text = six.u(
            'This message contains funny UTF16 characters like this one: '
            '"\xc2\xa0" and this one "\xe2\x9c\xbf".'
        )

        self.assertEqual(
            expected_text,
            actual_text,
        )

    def test_message_with_unknown_charset(self):
        """ Ensure that we gracefully fail at handling unknown encodings.

        Should an unknown encoding be used, we should:

        - Add a X-Django-Mailbox-Altered-Message header
        - Use UTF-8 (with replacement) as the de-facto (and probably incorrect)
          encoding for this payload part.

        """
        email_object = self._get_email_object(
            'message_with_invalid_payload_encoding.eml'
        )

        msg = self.mailbox.process_incoming_message(email_object)

        actual_body = msg.get_text_body()

        expected_body = six.u(
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd '
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd'
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd '
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd '
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd'
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd '
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd'
            '\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd.'
        )

        self.assertEqual(
            expected_body,
            actual_body,
        )

    def test_message_with_invalid_content_for_declared_encoding(self):
        """ Ensure that we gracefully handle mis-encoded bodies.

        Should a payload body be misencoded, we should:

        - Decode the message (with replacement) using the declared encoding.
        - Always return a payload body in the declared encoding, using python's
          usual replacement mechanisms.

        """
        email_object = self._get_email_object(
            'message_with_invalid_content_for_declared_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        actual_body = msg.get_text_body()
        expected_body = '??? ????????? ????? ???????????? ?????????.'

        self.assertEqual(
            actual_body,
            expected_body,
        )
