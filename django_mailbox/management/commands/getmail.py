import logging

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        Mailbox.get_new_mail_all_mailboxes(args)
