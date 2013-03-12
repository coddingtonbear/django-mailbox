import email
import os.path
import shutil

from django.db import models
from django.test import TestCase

import django_mailbox
from django_mailbox.models import Mailbox, Message

class EmailMessageTestCase(TestCase):
    def _get_email_object(self, name):
        with open(os.path.join(os.path.dirname(__file__), name), 'r') as f:
            return email.message_from_string(
                f.read()
            )

    def tearDown(self):
        for message in Message.objects.all():
            message.delete()

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
            '<CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>'
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

        self.assertEquals(
            expected_count,
            actual_count,
        )

        attachment = msg.attachments.all()[0]
        self.assertEquals(
            os.path.basename(attachment.document.name),
            'heart.png',
        )

    def test_message_get_text_body(self):
        message = self._get_email_object('multipart_text.eml')

        mailbox = Mailbox.objects.create()
        msg = mailbox.process_incoming_message(message)

        expected_results = 'Hello there!'
        actual_results = msg.get_text_body().strip()

        self.assertEquals(
            expected_results,
            actual_results,
        )

class TestFilterMessageBody(EmailMessageTestCase):
    def setUp(self):
        django_mailbox.models.STRIP_UNALLOWED_MIMETYPES = True
        super(TestFilterMessageBody, self).setUp()

    def tearDown(self):
        django_mailbox.models.STRIP_UNALLOWED_MIMETYPES = False
        super(TestFilterMessageBody, self).tearDown()

    def test_filter_message_does_not_filter_message_if_disabled(self):
        django_mailbox.models.STRIP_UNALLOWED_MIMETYPES = False
        message = self._get_email_object('message_with_attachment.eml')
        mailbox = Mailbox.objects.create()

        self.assertEquals(
            message.as_string(),
            mailbox._filter_message_body(message).as_string()
        )

    def test_filter_message_removes_unknown_content_if_disabled(self):
        # The below is the _same_ as message_with_attachment.eml, but missing
        # its attached png image, and adding the expected message altered header.
        message_without_non_plaintext = (
            "MIME-Version: 1.0\n"
            "Received: by 10.221.0.211 with HTTP; Sun, 20 Jan 2013 12:07:07 -0800 (PST)\n"
            "X-Originating-IP: [24.22.122.177]\n"
            "Date: Sun, 20 Jan 2013 12:07:07 -0800\n"
            "Delivered-To: test@adamcoddington.net\n"
            "Message-ID: <CAMdmm+jYCgrxrekAxszmDnBjAytcBym-Ec+uM-+HEtzuKy=M_g@mail.gmail.com>\n"
            "Subject: Message With Attachment\n"
            "From: Adam Coddington <test@adamcoddington.net>\n"
            "To: Adam Coddington <test@adamcoddington.net>\n"
            "Content-Type: multipart/mixed; boundary=047d7b33dd729737fe04d3bde348\n"
            "X-Django-Mailbox-Altered-Message: Stripped image/png*1, multipart/mixed*1\n"
            "\n--047d7b33dd729737fe04d3bde348\n"
            "Content-Type: text/plain; charset=UTF-8\n\n"
            "This message has an attachment.\n\n--047d7b33dd729737fe04d3bde348--"
        )
        message = self._get_email_object('message_with_attachment.eml')
        mailbox = Mailbox.objects.create()

        self.assertEquals(
            message_without_non_plaintext,
            mailbox._filter_message_body(message).as_string()
        )
