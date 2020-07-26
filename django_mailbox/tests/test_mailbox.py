import os

from django.test import TestCase

from django_mailbox.models import Mailbox


__all__ = ['TestMailbox']


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

    def test_last_polling_field_exists(self):
        mailbox = Mailbox()
        self.assertTrue(hasattr(mailbox, 'last_polling'))

    def test_get_new_mail_update_last_polling(self):
        mailbox = Mailbox.objects.create(uri="mbox://" + os.path.join(
                os.path.dirname(__file__),
                'messages',
                'generic_message.eml',
            ))
        self.assertEqual(mailbox.last_polling, None)
        list(mailbox.get_new_mail())
        self.assertNotEqual(mailbox.last_polling, None)

    def test_queryset_get_new_mail(self):
        mailbox = Mailbox.objects.create(uri="mbox://" + os.path.join(
                os.path.dirname(__file__),
                'messages',
                'generic_message.eml',
            ))
        Mailbox.objects.filter(pk=mailbox.pk).get_new_mail()
        mailbox.refresh_from_db()
        self.assertNotEqual(mailbox.last_polling, None)
