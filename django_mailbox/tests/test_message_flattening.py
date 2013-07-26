from django_mailbox import models
from django_mailbox.models import Message
from django_mailbox.tests.base import EmailMessageTestCase


__all__ = ['TestMessageFlattening']


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
