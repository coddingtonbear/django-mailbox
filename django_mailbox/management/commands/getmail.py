import logging

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    args = ""
    help = ""

    def add_arguments(self, parser):
        parser.add_argument('--logging', type=bool, default=True, dest='logging',
                            help='Enable logging (default true)')

    def handle(self, *args, **options):
        mailboxes = Mailbox.active_mailboxes.all()
        if args:
            mailboxes = mailboxes.filter(
                name=' '.join(args)
            )
        for mailbox in mailboxes:
            if options['logging']:
                logger.info(
                    'Gathering messages for %s',
                    mailbox.name
                )
            messages = mailbox.get_new_mail()
            for message in messages:
                if options['logging']:
                    logger.info(
                        'Received %s (from %s)',
                        message.subject,
                        message.from_address
                    )
