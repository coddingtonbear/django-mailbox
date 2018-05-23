from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


class Command(BaseCommand):
    help = 'Sends an e-mail to specified recipient'

    def add_arguments(self, parser):
        parser.add_argument('from', type=int, help='ID (pk) for the mailbox you want to use to send an e-mail')
        parser.add_argument('to', help='E-mail address of recipient')
        parser.add_argument('subject', help='Subject of letter')
        parser.add_argument('body', help='Message')

    def handle(self, *args, **options):

        from_email = options.get('from')
        to = options.get('to')
        subject = options.get('subject')
        body = options.get('body')

        mailbox = Mailbox.objects.get(pk=from_email)
        self.stdout.write(self.style.WARNING("-"*36 + "\nFrom:    %s \nTo:      %s \nSubject: %s \nMessage: %s \n" %
                                             (mailbox.from_email,
                                             to, subject, body) + '-'*36))
        if mailbox.send_mail(options.get('subject'), options.get('to'), options.get('body')):
            self.stdout.write(self.style.SUCCESS('The letter is sent.'))
