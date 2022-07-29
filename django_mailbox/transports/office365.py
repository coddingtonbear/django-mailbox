import O365
import logging

from django.conf import settings

from .base import EmailTransport, MessageParseError

logger = logging.getLogger(__name__)


class Office365Transport(EmailTransport):
    def __init__(
        self, hostname, username, port=None, ssl=False, tls=False, folder=None
    ):
        self.max_message_size = getattr(
            settings,
            'DJANGO_MAILBOX_MAX_MESSAGE_SIZE',
            False
        )
        self.integration_testing_subject = getattr(
            settings,
            'DJANGO_MAILBOX_INTEGRATION_TESTING_SUBJECT',
            None
        )
        self.hostname = hostname
        self.username = username
        self.port = port
        self.folder = folder
        self.tls = tls
        if ssl:
             #self.transport = imaplib.IMAP4_SSL
            if not self.port:
                self.port = 993
        else:
            #self.transport = imaplib.IMAP4
            if not self.port:
                self.port = 143

    def connect(self, client_id, client_secret, tenant_id):
        credentials = (client_id, client_secret)

        self.account = O365.Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
        self.account.authenticate()

        self.mailbox = self.account.mailbox(resource=self.username)
        self.mailbox_folder = self.mailbox.inbox_folder()
        if self.folder:
            self.mailbox_folder = self.mailbox.get_folder(folder_name=self.folder)

    def get_message(self, condition=None):
        for message in self.mailbox.get_messages(order_by='receivedDateTime'):
            try:
                mime_content = message.get_mime_content()
                message = self.get_email_from_bytes(mime_content)

                if condition and not condition(message):
                    continue

                yield message
            except MessageParseError:
                continue
        return

