import os.path
import sys

import mock
import six

from django_mailbox.models import Mailbox, Message
from django_mailbox.utils import convert_header_to_unicode
from django_mailbox.tests.base import EmailMessageTestCase
from django.core.mail import EmailMessage


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

    def test_message_with_encoded_attachment_filenames(self):
        message = self._get_email_object(
            'message_with_koi8r_filename_attachments.eml'
        )

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        attachments = msg.attachments.order_by('pk').all()
        self.assertEqual(
            u'\u041f\u0430\u043a\u0435\u0442 \u043f\u0440\u0435\u0434\u043b'
            u'\u043e\u0436\u0435\u043d\u0438\u0439 HSE Career Fair 8 \u0430'
            u'\u043f\u0440\u0435\u043b\u044f 2016.pdf',
            attachments[0].get_filename()
        )
        self.assertEqual(
            u'\u0412\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438.pdf',
            attachments[1].get_filename()
        )
        self.assertEqual(
            u'\u041f\u0430\u043a\u0435\u0442 \u043f\u0440\u0435\u0434\u043b'
            u'\u043e\u0436\u0435\u043d\u0438\u0439 2016.pptx',
            attachments[2].get_filename()
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

    def test_message_with_not_decoded_attachment_header(self):
        if sys.version_info > (3, 0):
            self.skipTest(
                "This test is only relevant on Python 2.x."
            )

        email_object = self._get_email_object(
            'message_with_not_decoded_attachment_header.eml',
        )

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(email_object)

        expected_count = 1
        actual_count = msg.attachments.count()

        self.assertEqual(
            expected_count,
            actual_count,
        )

        attachment = msg.attachments.all()[0]
        self.assertEqual(
            attachment.get_filename(),
            u'\xc3\xb0\xcc\x9eo\xce\xb2\xcc\x9ele.png',
        )

    def test_message_get_text_body(self):
        message = self._get_email_object('multipart_text.eml')

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        expected_results = 'Hello there!'
        actual_results = msg.text.strip()

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

        actual_text = message.text
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

    def test_message_issue_82(self):
        """ Ensure that we properly handle incorrectly encoded messages

        """
        email_object = self._get_email_object('email_issue_82.eml')
        it = 'works'
        try:
            # it's ok to call as_string() before passing email_object
            # to _get_dehydrated_message()
            email_object.as_string()
        except:
            it = 'do not works'

        success = True
        try:
            msg = self.mailbox.process_incoming_message(email_object)
        except ValueError:
            success = False

        self.assertEqual(it, 'works')
        self.assertEqual(True, success)

    def test_message_issue_82_bis(self):
        """ Ensure that the email object is good before and after
        calling _get_dehydrated_message()

        """
        message = self._get_email_object('email_issue_82.eml')

        success = True

        # this is the code of _process_message()
        msg = Message()
        # if STORE_ORIGINAL_MESSAGE:
        #     msg.eml.save('%s.eml' % uuid.uuid4(), ContentFile(message), save=False)
        msg.mailbox = self.mailbox
        if 'subject' in message:
            msg.subject = convert_header_to_unicode(message['subject'])[0:255]
        if 'message-id' in message:
            msg.message_id = message['message-id'][0:255]
        if 'from' in message:
            msg.from_header = convert_header_to_unicode(message['from'])
        if 'to' in message:
            msg.to_header = convert_header_to_unicode(message['to'])
        elif 'Delivered-To' in message:
            msg.to_header = convert_header_to_unicode(message['Delivered-To'])
        msg.save()

        #here the message is ok
        str_msg = message.as_string()
        message = self.mailbox._get_dehydrated_message(message, msg)
        try:
            # here as_string raises UnicodeEncodeError
            str_msg = message.as_string()
        except:
            success = False

        msg.set_body(str_msg)
        if message['in-reply-to']:
            try:
                msg.in_reply_to = Message.objects.filter(
                    message_id=message['in-reply-to']
                )[0]
            except IndexError:
                pass
        msg.save()

        self.assertEqual(True, success)

    def test_message_with_misplaced_utf8_content(self):
        """ Ensure that we properly handle incorrectly encoded messages

        ``message_with_utf8_char.eml``'s primary text payload is marked
        as being iso-8859-1 data, but actually contains UTF-8 bytes.

        """
        email_object = self._get_email_object('message_with_utf8_char.eml')

        msg = self.mailbox.process_incoming_message(email_object)

        expected_text = six.u(
            'This message contains funny UTF16 characters like this one: '
            '"\xc2\xa0" and this one "\xe2\x9c\xbf".'
        )
        actual_text = msg.text

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

        msg.text

    def test_message_with_valid_content_in_single_byte_encoding(self):
        email_object = self._get_email_object(
            'message_with_single_byte_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        actual_text = msg.text
        expected_body = six.u(
            '\u042d\u0442\u043e '
            '\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 '
            '\u0438\u043c\u0435\u0435\u0442 '
            '\u043d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d'
            '\u0443\u044e '
            '\u043a\u043e\u0434\u0438\u0440\u043e\u0432\u043a\u0430.'
        )

        self.assertEqual(
            actual_text,
            expected_body,
        )

    def test_message_with_single_byte_subject_encoding(self):
        email_object = self._get_email_object(
            'message_with_single_byte_extended_subject_encoding.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        expected_subject = six.u(
            '\u00D3\u00E7\u00ED\u00E0\u00E9 \u00EA\u00E0\u00EA '
            '\u00E7\u00E0\u00F0\u00E0\u00E1\u00E0\u00F2\u00FB\u00E2'
            '\u00E0\u00F2\u00FC \u00EE\u00F2 1000$ \u00E2 '
            '\u00ED\u00E5\u00E4\u00E5\u00EB\u00FE!'
        )
        actual_subject = msg.subject
        self.assertEqual(actual_subject, expected_subject)

        if sys.version_info >= (3, 3):
            # There were various bugfixes in Py3k's email module,
            # this is apparently one of them.
            expected_from = six.u('test test <mr.test32@mail.ru>')
        else:
            expected_from = six.u('test test<mr.test32@mail.ru>')
        actual_from = msg.from_header

        self.assertEqual(expected_from, actual_from)

    def test_message_reply(self):
        email_object = EmailMessage('Test subject',  # subject
            'Test body',  # body
            'username@example.com',  # from
            ['mr.test32@mail.ru'],  # to
        )
        msg = self.mailbox.record_outgoing_message(email_object.message())

        self.assertTrue(msg.outgoing)

        actual_from = 'username@example.com'
        reply_email_object = EmailMessage(
            'Test subject',  # subject
            'Test body',  # body
            actual_from,  # from
            ['mr.test32@mail.ru'],  # to
        )

        with mock.patch.object(reply_email_object, 'send'):
            reply_msg = msg.reply(reply_email_object)

        self.assertEqual(reply_msg.in_reply_to, msg)

        self.assertEqual(actual_from, msg.from_header)

        reply_email_object.from_email = None

        with mock.patch.object(reply_email_object, 'send'):
            second_reply_msg = msg.reply(reply_email_object)

        self.assertEqual(self.mailbox.from_email, second_reply_msg.from_header)

    def test_message_with_text_attachment(self):
        email_object = self._get_email_object(
            'message_with_text_attachment.eml',
        )

        msg = self.mailbox.process_incoming_message(email_object)

        self.assertEqual(msg.attachments.all().count(), 1)
