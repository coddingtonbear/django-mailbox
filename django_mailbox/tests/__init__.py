import email
import os.path
import shutil

from django.db import models
from django.test import TestCase

from django_mailbox.models import Mailbox

class TestProcessMessage(TestCase):
    def _get_email_object(self, name):
        with open(os.path.join(os.path.dirname(__file__), name), 'r') as f:
            return email.message_from_string(
                f.read()
            )

    def tearDown(self):
        try:
            shutil.rmtree('mailbox_attachments')
        except OSError:
            pass
    
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
