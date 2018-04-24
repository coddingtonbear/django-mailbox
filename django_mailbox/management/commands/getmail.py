import logging

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox, Message

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def message_not_in_database(message):
    if Message.objects.filter(message_id__iexact=message['message-id']).exists():
        return False
    return True


class Command(BaseCommand):
    def handle(self, *args, **options):
        mailboxes = Mailbox.active_mailboxes.all()
        if args:
            mailboxes = mailboxes.filter(
                name=' '.join(args)
            )
        for mailbox in mailboxes:
            logger.info(
                'Gathering messages for %s',
                mailbox.name
            )

            messages = mailbox.get_new_mail(condition=message_not_in_database)
            for message in messages:
                logger.info(
                    'Received %s (from %s)',
                    message.subject,
                    message.from_address
                )
