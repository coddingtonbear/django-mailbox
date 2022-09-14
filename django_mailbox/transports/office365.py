import logging
import urllib3
import json

from django_mailbox.transports.imap import ImapTransport
from django.conf import settings


logger = logging.getLogger(__name__)


class Office365ImapTransport(ImapTransport):
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
        # for office365 access

        access_token = None
        while access_token is None:
            try:
                access_token = self.get_office365_access_token()
            except Exception as e:
                raise ValueError(
                    f"Could not acquire the access token for {username} exception details={e}"
                )

        auth_string = 'user={}\1auth=Bearer {}\1\1'.format(
            username,
            access_token
        )

        self.server = self.transport(self.hostname, self.port)
        logger.info(f'[_connect_oauth] hostname = {self.hostname}')
        logger.info(f'[_connect_oauth] auth string is: {auth_string}')
        typ, dat = self.server.authenticate("XOAUTH2", lambda x: auth_string)
        logger.info(f'[_connect_oauth] auth string is: {auth_string} and typ={typ} dat={dat}')
        self.server.select()

    def get_office365_access_token(self):
        url = f"https://login.microsoftonline.com/{settings.MICROSOFT_O365_TENENT_ID}/oauth2/v2.0/token"
        oauth_params = {
            "client_id": settings.MICROSOFT_O365_CLIENT_ID,
            "client_secret": settings.MICROSOFT_O365_CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        }
        http = urllib3.PoolManager()
        response = http.request("POST", url, oauth_params)
        if response.status == 200:
            token = json.loads(response.data).get("access_token")
            logger.info(f"[get_office365_access_token] token aquired")
            return token
        else:
            raise Exception(
                f"[get_office365_access_token] Failed to authenticate with O365 {response.data}"
            )