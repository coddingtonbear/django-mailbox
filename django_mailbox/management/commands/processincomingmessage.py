import email
import ipdb
import sys

from django.core.managemet.base import BaseCommand

from django_mailbox.models import Mailbox, Message

class Command(BaseCommand):
    def handle(self, *args, **options):
        message_string = open(sys.stdin, 'r').read()
        ipdb.set_trace()
        #message = email.message_from_string(message_string)

