from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox

class Command(BaseCommand):
    def handle(self, *args, **options):
        mailboxes = Mailbox.active_mailboxes.all()
        if args:
            mailboxes = mailboxes.filter(name = ' '.join(args))
        for mailbox in mailboxes:
            self.stdout.write('Gathering messages for %s\n' % mailbox.name)
            messages = mailbox.get_new_mail()
            for message in messages:
                self.stdout.write('Received %s (from %s)\n' % (
                        message.subject,
                        message.from_address
                    ))
