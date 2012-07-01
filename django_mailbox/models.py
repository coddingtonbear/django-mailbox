import email
import rfc822
import urllib
import urlparse

from django.db import models
from django_mailbox.transports import Pop3Transport, ImapTransport,\
        MaildirTransport, MboxTransport, BabylTransport, MHTransport, \
        MMDFTransport
from django_mailbox.signals import message_received

class Mailbox(models.Model):
    name = models.CharField(max_length=255)
    uri = models.CharField(
            max_length=255,
            help_text="""
                Example: imap+ssl://myusername:mypassword@someserver
                <br />
                <br />
                Internet transports include 'imap' and 'pop3'; common local file transports include 'maildir', 'mbox', and less commonly 'babyl', 'mh', and 'mmdf'.
                <br />
                <br />
                Be sure to urlencode your username and password should they 
                contain illegal characters (like @, :, etc).
                """
            )

    @property
    def _protocol_info(self):
        return urlparse.urlparse(self.uri)

    @property
    def _domain(self):
        return self._protocol_info.hostname

    @property
    def port(self):
        return self._protocol_info.port

    @property
    def username(self):
        return urllib.unquote(self._protocol_info.username)

    @property
    def password(self):
        return urllib.unquote(self._protocol_info.password)

    @property
    def location(self):
        return self._domain if self._domain else '' + self._protocol_info.path

    @property
    def type(self):
        scheme = self._protocol_info.scheme.lower()
        if '+' in scheme:
            return scheme.split('+')[0]
        return scheme

    @property
    def use_ssl(self):
        return '+ssl' in self._protocol_info.scheme.lower()

    def get_connection(self):
        if self.type == 'imap':
            conn = ImapTransport(
                        self.location,
                        port=self.port if self.port else None,
                        ssl=self.use_ssl
                    )
            conn.connect(self.username, self.password)
        elif self.type == 'pop3':
            conn = Pop3Transport(
                        self.location,
                        port=self.port if self.port else None,
                        ssl=self.use_ssl
                    )
            conn.connect(self.username, self.password)
        elif self.type == 'maildir':
            conn = MaildirTransport(self.location)
        elif self.type == 'mbox':
            conn = MboxTransport(self.location)
        elif self.type == 'babyl':
            conn = BabylTransport(self.location)
        elif self.type == 'mh':
            conn = MHTransport(self.location)
        elif self.type == 'mmdf':
            conn = MMDFTransport(self.location)
        return conn

    def get_new_mail(self):
        connection = self.get_connection()
        new_mail = []
        for message in connection.get_message():
            msg = Message()
            print msg
            msg.mailbox = self
            msg.subject = message['subject'][0:255]
            msg.message_id = message['message-id'][0:255]
            msg.from_address = rfc822.parseaddr(message['from'])[1][0:255]
            msg.body = message.as_string()
            msg.save()
            new_mail.append(msg)
            message_received.send(sender=self, message=msg)
        return new_mail

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Mailboxes"

class Message(models.Model):
    mailbox = models.ForeignKey(Mailbox, related_name='messages')
    subject = models.CharField(max_length=255)
    message_id = models.CharField(max_length=255)
    from_address = models.CharField(max_length=255)

    body = models.TextField()

    received = models.DateTimeField(
            auto_now_add=True
            )

    def get_email_object(self):
        return email.message_from_string(self.body)

    def __unicode__(self):
        return self.subject
