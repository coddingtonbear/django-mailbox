import logging

from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-mb', '--mailboxes', type=str, nargs='+', help='Write mailbox names')
        parser.add_argument('-mr', '--max_read', type=int,
                            help='Write maximum number of email to read from each mailbox')

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        Mailbox.get_new_mail_all_mailboxes(options)
