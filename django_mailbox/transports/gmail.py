from imaplib import IMAP4, IMAP4_SSL

from .base import EmailTransport, MessageParseError


class GmailTransport(EmailTransport):
    def __init__(self, hostname, port=None, ssl=True):
        self.hostname = hostname
        self.port = port
        self.exclusive = False
        self.MAX_MSG_SIZE = 2000000
        if ssl:
            self.transport = IMAP4_SSL
            if not self.port:
                self.port = 993
        else:
            self.transport = IMAP4
            if not self.port:
                self.port = 143

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
        typ, msg = self.server.login(username, password)
        self.server.select()

    def _connect_oauth(self, username, refresh_token):
        import oauth2
        client_id = "REDACTED"
        client_secret = "REDACTED"
        response = oauth2.RefreshToken(client_id, client_secret, refresh_token)
        access_token = response['access_token']
        print "New Access Token :", access_token
        print "Expires in :", response['expires_in']
        # before passing into IMAPLib access token needs to be converted
        # into a string
        oauth2String = oauth2.GenerateOAuth2String(
            username,
            access_token,
            base64_encode=False
        )
        self.server = self.transport(self.hostname, self.port)
        self.server.authenticate('XOAUTH2', lambda x: oauth2String)
        self.server.select()

    def _get_all_message_ids(self):
        response, message_ids = self.server.search(None, 'ALL', )
        return message_ids[0].split(' ')

    def _get_unread_message_ids(self):
        response, message_ids = self.server.uid('search', None, 'UNSEEN', )
        return message_ids[0].split(' ')

    def _archive_message(self, uid):
        # Move to "[Gmail]/All Mail" folder
        pass

    def _trash_message(self, uid):
        # Move to "[Gmail]/Trash"
        pass

    def _delete_message(self, uid):
        # add Deleted Flag
        self.server.store(uid, "+FLAGS", "\\Deleted")

    def _get_small_message_ids(self, message_ids):
        safe_message_ids = []

        status, data = self.server.uid(
            'fetch',
            ','.join(message_ids),
            '(BODY.PEEK[HEADER] RFC822.SIZE BODYSTRUCTURE)'
            )

        for each_msg in data:
            if isinstance(each_msg, tuple):
                try:
                    metadata, structure = each_msg[0].split(' BODYSTRUCTURE ')
                    uid = metadata.split('(')[1].split(' ')[1]
                    size = metadata.split('(')[1].split(' ')[3]
                    if int(size) <= int(self.MAX_MSG_SIZE):
                        safe_message_ids.append(uid)
                except ValueError, e:
                    print "ValueError: %s working on %s" % (e, each_msg[0])
                    print each_msg
                    pass
        return safe_message_ids

    def get_message(self):
        # Fetch a list of message uids to process
        if self.exclusive:
            message_ids = self._get_all_message_ids()
        else:
            message_ids = self._get_unread_message_ids()
        print "There are %s messages: %s" % (len(message_ids), message_ids)
        if self.MAX_MSG_SIZE:
            message_ids = self._get_small_message_ids(message_ids)

        if not message_ids:
            return

        for uid in message_ids:
            try:
                typ, msg_contents = self.server.uid('fetch', uid, '(RFC822)')
                message = self.get_email_from_bytes(msg_contents[0][1])
                yield message
            except MessageParseError:
                continue
            if self.exclusive:
                self.server.store(uid, "+FLAGS", "\\Deleted")
        self.server.expunge()
        return
