import logging

from django_mailbox.transports.imap import ImapTransport


logger = logging.getLogger(__name__)


class GmailImapTransport(ImapTransport):

    def connect(self, username, password):
        # Try to use oauth2 first.  It's much safer
        try:
            self._connect_oauth(username)
        except (TypeError, ValueError) as e:
            logger.warning("Couldn't do oauth2 because %s" % e)
            self.server = self.transport(self.hostname, self.port)
            typ, msg = self.server.login(username, password)
            self.server.select()

    def _connect_oauth(self, username):
        # username should be an email address that has already been authorized
        # for gmail access
        try:
            from django_mailbox.google_utils import (
                get_google_access_token,
                fetch_user_info,
                AccessTokenNotFound,
            )
        except ImportError:
            raise ValueError(
                "Install python-social-auth to use oauth2 auth for gmail"
            )

        access_token = None
        while access_token is None:
            try:
                access_token = get_google_access_token(username)
                google_email_address = fetch_user_info(username)['email']
            except TypeError:
                # This means that the google process took too long
                # Trying again is the right thing to do
                pass
            except AccessTokenNotFound:
                raise ValueError(
                    "No Token available in python-social-auth for %s" % (
                        username
                    )
                )

        auth_string = 'user={}\1auth=Bearer {}\1\1'.format(
            google_email_address,
            access_token
        )
        self.server = self.transport(self.hostname, self.port)
        self.server.authenticate('XOAUTH2', lambda x: auth_string)
        self.server.select()
