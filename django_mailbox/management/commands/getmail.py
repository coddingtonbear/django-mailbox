import logging

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        Mailbox.get_new_mail_all_mailboxes(args)
