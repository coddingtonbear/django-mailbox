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

    def _get_all_message_ids(self):
        typ, inbox = self.server.search(None, 'ALL', )

    def _get_unread_message_ids(self):
        typ, inbox = self.server.uid('search', None, 'UNSEEN', )

    def _archive_message(self, uid):
        #Move to "[Gmail]/All Mail" folder
        pass

    def _trash_message(self, uid):
        # Move to "[Gmail]/Trash"
        pass

    def _delete_message(self, uid):
        # add Deleted Flag
        self.server.store(key, "+FLAGS", "\\Deleted")

    def get_message(self):
        # Fetch a list of message uids to process
        if self.exclusive:
            typ, message_ids = self.get_all_message_ids()
        else:
            typ, message_ids = self.get_unread_message_ids()
        if self.MAX_MSG_SIZE:
            safe_message_ids = []
            status, data = mailbox.uid('fetch', ','.join(message_ids), '(BODY.PEEK[HEADER] RFC822.SIZE BODYSTRUCTURE)')
            for each_msg in data:
                metadata,structure = each[0].split(' BODYSTRUCTURE ')
                uid = metadata.split('(')[1].split(' ')[3]
                size = metadata.split('(')[1].split(' ')[5]
                if int(size) <= int(MAX_MSG_SIZE):
                    safe_message_ids.append(uid)
            message_ids = safe_msg_ids

        if not message_ids[0]:
            return

        for uid in message_ids[0].split():
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
