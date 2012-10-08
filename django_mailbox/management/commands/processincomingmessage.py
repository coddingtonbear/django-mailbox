import email
import logging
import rfc822
import sys

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
    def handle(self, *args, **options):
        message = email.message_from_string(sys.stdin.read())
        if message:
            mailbox = self.get_mailbox_for_message(message)
            mailbox.process_incoming_message(message)
            logger.info("Message received from %s" % message['from'])
        else:
            logger.warning("Message not processable.")

    def get_mailbox_for_message(self, message):
        email_address = rfc822.parseaddr(message['from'][1][0:255])
        mailbox, created = Mailbox.objects.get_or_create(
                name=email_address,
                )
        return mailbox
