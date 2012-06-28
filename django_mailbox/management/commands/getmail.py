from django.core.management.base import BaseCommand
from django.dispatch import receiver

from django_mailbox.models import Mailbox
from django_mailbox.signals import message_received

class Command(BaseCommand):
    def handle(self, *args, **options):
        mailboxes = Mailbox.objects.all()
        if args:
            mailboxes = mailboxes.filter(name = ' '.join(args))
        for mailbox in mailboxes:
            self.stdout.write('Gathering messages for %s\n' % mailbox.name)
            mailbox.get_new_mail()

    @receiver(message_received)
    def incoming_message(self, sender, message, **kwargs):
        self.stdout.write('Received %s\n' % message.subject)
