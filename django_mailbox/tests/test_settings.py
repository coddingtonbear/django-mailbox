from django.test import TestCase
from django.conf import settings
from django_mailbox.models import ATTACHMENT_UPLOAD_TO


class TestSettings(TestCase):
    def test_default_attachment_upload_to(self):
        user_setting = getattr(settings, 'DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO', False)
        self.assertFalse(user_setting)
        self.assertEqual(ATTACHMENT_UPLOAD_TO, 'mailbox_attachments/%Y/%m/%d/')
