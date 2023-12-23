import logging

from django.conf import settings

from .base import EmailTransport, MessageParseError

logger = logging.getLogger(__name__)


class Office365Transport(EmailTransport):
    def __init__(
        self, hostname, username, archive='', folder=None
    ):
        self.integration_testing_subject = getattr(
            settings,
            'DJANGO_MAILBOX_INTEGRATION_TESTING_SUBJECT',
            None
        )
        self.hostname = hostname
        self.username = username
        self.archive = archive
        self.folder = folder

    def connect(self, client_id, client_secret, tenant_id):
        try:
            import O365
        except ImportError:
            raise ValueError(
                "Install o365 to use oauth2 auth for office365"
            )

        credentials = (client_id, client_secret)

        self.account = O365.Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
        self.account.authenticate()

        self.mailbox = self.account.mailbox(resource=self.username)
        self.mailbox_folder = self.mailbox.inbox_folder()
        if self.folder:
            self.mailbox_folder = self.mailbox.get_folder(folder_name=self.folder)

    def get_message(self, condition=None):
        archive_folder = None
        if self.archive:
            archive_folder = self.mailbox.get_folder(folder_name=self.archive)
            if not archive_folder:
                archive_folder = self.mailbox.create_child_folder(self.archive)

        for o365message in self.mailbox_folder.get_messages(order_by='receivedDateTime'):
            try:
                mime_content = o365message.get_mime_content()
                message = self.get_email_from_bytes(mime_content)

                if condition and not condition(message):
                    continue

                yield message
            except MessageParseError:
                continue

            if self.archive and archive_folder:
                o365message.copy(archive_folder)

            o365message.delete()
        return
