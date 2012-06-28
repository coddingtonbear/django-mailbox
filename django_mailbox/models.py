import email
import rfc822
import urllib
import urlparse

from django.db import models
from django_mailbox.transports import PopMailEnumerator, ImapMailEnumerator
from django_mailbox.signals import message_received

class Mailbox(models.Model):
    name = models.CharField(max_length=255)
    uri = models.CharField(
            max_length=255,
            help_text="""
                Start your URI with imap:// or pop3://.
                <br />
                <br />
                Example: imap://myusername:mypassword@someserver
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
        return self._protocol_info.scheme.lower()

    def get_connection(self):
        if self.type == 'imap':
            conn = ImapMailEnumerator(
                        self.location,
                        self.port if self.port else 143
                    )
        elif self.type == 'pop3':
            conn = PopMailEnumerator(
                        self.location,
                        self.port if self.port else 110
                    )
        conn.connect(self.username, self.password)
        return conn

    def get_new_mail(self):
        connection = self.get_connection()
        new_mail = []
        for message in connection.get_message():
            msg = Message()
            msg.mailbox = self
            msg.subject = message['subject']
            msg.message_id = message['message-id']
            msg.from_address = rfc822.parseaddr(message['from'])[1]
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
