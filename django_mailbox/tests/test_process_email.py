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

    def test_message_with_invalid_content_for_declared_encoding(self):
        """ Ensure that we gracefully handle mis-encoded bodies.

        Should a payload body be misencoded, we should:

        - Not explode

        Note: there is (intentionally) no assertion below; the only guarantee
        we make via this library is that processing this e-mail message will
        not cause an exception to be raised.

        """
        email_object = self._get_email_object(
            'message_with_invalid_content_for_declared_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        msg.get_text_body()

    def test_message_with_valid_content_in_single_byte_encoding(self):
        email_object = self._get_email_object(
            'message_with_single_byte_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        actual_body = msg.get_text_body()

        expected_body = six.u(
            '\u042d\u0442\u043e '
            '\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 '
            '\u0438\u043c\u0435\u0435\u0442 '
            '\u043d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d'
            '\u0443\u044e '
            '\u043a\u043e\u0434\u0438\u0440\u043e\u0432\u043a\u0430.'
        )

        self.assertEqual(
            actual_body,
            expected_body,
        )

    def test_message_with_single_byte_subject_encoding(self):
        email_object = self._get_email_object(
            'message_with_single_byte_extended_subject_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        expected_subject = (
            u'\xd3\xe7\xed\xe0\xe9 \xea\xe0\xea \xe7\xe0\xf0'
            u'\xe0\xe1\xe0\xf2\xfb\xe2\xe0\xf2\xfc \xee\xf2 1000$ '
            u'\xe2 \xed\xe5\xe4\xe5\xeb\xfe!'
        )
        actual_subject = msg.subject
        self.assertEqual(actual_subject, expected_subject)

        expected_from = u'test test<mr.test32@mail.ru>'
        actual_from = msg.from_header

        self.assertEqual(expected_from, actual_from)
