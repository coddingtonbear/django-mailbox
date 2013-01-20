import email
from email.utils import formatdate
import rfc822
import urllib
import urlparse
import os

from django.conf import settings
from django.core.mail.message import make_msgid
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django_mailbox.transports import Pop3Transport, ImapTransport,\
        MaildirTransport, MboxTransport, BabylTransport, MHTransport, \
        MMDFTransport
from django_mailbox.signals import message_received

class ActiveMailboxManager(models.Manager):
    def get_query_set(self):
        return super(ActiveMailboxManager, self).get_query_set().filter(
            active=True,
        )

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
                """,
            blank=True,
            null=True,
            default=None,
            )
    from_email = models.CharField(
            max_length=255,
            help_text="""
                Example: MailBot &lt;mailbot@yourdomain.com&gt;
                <br />
                'From' header to set for outgoing email.
                <br />
                <br />
                If you do not use this e-mail inbox for outgoing mail, this 
                setting is unnecessary.
                <br />
                If you send e-mail without setting this, your 'From' header will
                be set to match the setting `DEFAULT_FROM_EMAIL`.
            """,
            blank=True,
            null=True,
            default=None,
            )
    active = models.BooleanField(
            help_text="""
                Check this e-mail inbox for new e-mail messages during polling
                cycles.  This checkbox does not have an effect upon whether
                mail is collected here when this mailbox receives mail from a
                pipe, and does not affect whether e-mail messages can be
                dispatched from this mailbox.
            """,
            blank=True,
            default=True,
            )

    objects = models.Manager()
    active_mailboxes = ActiveMailboxManager()

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
        if not self.uri:
            return None
        elif self.type == 'imap':
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

    def process_incoming_message(self, message):
        msg = self._process_message(message)
        msg.outgoing = False
        msg.save()
        message_received.send(sender=self, message=msg)
        return msg

    def record_outgoing_message(self, message):
        msg = self._process_message(message)
        msg.outgoing = True
        msg.save()
        return msg

    def _process_message(self, message):
        msg = Message()
        msg.mailbox = self
        msg.subject = message['subject'][0:255]
        msg.message_id = message['message-id'][0:255]
        msg.from_header = message['from']
        msg.to_header = message['to']
        msg.body = message.as_string()
        if message['in-reply-to']:
            try:
                msg.in_reply_to = Message.objects.filter(message_id=message['in-reply-to'])[0]
            except IndexError:
                pass
        msg.save()
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                # ignore SMIME extension
                filename_basename, filename_extension = os.path.splitext(filename)
                if filename_extension in ('.p7s',):
                    continue
                data = part.get_payload(decode=True)
                if not data:
                    continue
                temp_file = NamedTemporaryFile(delete=True)
                temp_file.write(data)
                temp_file.flush()
                attachment = MessageAttachment()
                attachment.document.save(filename, File(temp_file))
                attachment.save()
                msg.attachments.add(attachment)
        return msg

    def get_new_mail(self):
        new_mail = []
        connection = self.get_connection()
        if not connection:
            return new_mail
        for message in connection.get_message():
            msg = self.process_incoming_message(message)
            new_mail.append(msg)
        return new_mail

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Mailboxes"

class IncomingMessageManager(models.Manager):
    def get_query_set(self):
        return super(IncomingMessageManager, self).get_query_set().filter(
            outgoing=False,
        )

class OutgoingMessageManager(models.Manager):
    def get_query_set(self):
        return super(OutgoingMessageManager, self).get_query_set().filter(
            outgoing=True,
        )

class UnreadMessageManager(models.Manager):
    def get_query_set(self):
        return super(UnreadMessageManager, self).get_query_set().filter(
            read=None
        )

class MessageAttachment(models.Model):
    document = models.FileField(upload_to='mailbox_attachments/%Y/%m/%d/')

    def __unicode__(self):
        return self.document.url

class Message(models.Model):
    mailbox = models.ForeignKey(Mailbox, related_name='messages')
    subject = models.CharField(max_length=255)
    message_id = models.CharField(max_length=255)
    in_reply_to = models.ForeignKey(
        'django_mailbox.Message', 
        related_name='replies',
        blank=True,
        null=True,
    )
    from_header = models.CharField(
        max_length=255,
    )
    to_header = models.TextField()
    outgoing = models.BooleanField(
        default=False,
        blank=True,
    )

    body = models.TextField()

    processed = models.DateTimeField(
        auto_now_add=True
    )
    read = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
    )

    attachments = models.ManyToManyField(
        MessageAttachment,
        blank=True,
    )

    objects = models.Manager()
    unread_messages = UnreadMessageManager()
    incoming_messages = IncomingMessageManager()
    outgoing_messages = OutgoingMessageManager()

    @property
    def address(self):
        """Property allowing one to get the relevant address(es).
        
        In earlier versions of this library, the model had an `address` field
        storing the e-mail address from which a message was received.  During
        later refactorings, it became clear that perhaps storing sent messages
        would also be useful, so the address field was replaced with two
        separate fields.
        
        """
        if self.outgoing:
            return self.to_addresses()
        else:
            return self.from_addresses()

    @property
    def from_address(self):
        return rfc822.parseaddr(self.from_header)[1]

    @property
    def to_addresses(self):
        addresses = []
        for address in self.to_header.split(','):
            addresses.append(
                    rfc822.parseaddr(
                            address
                        )[1]
                )
        return addresses

    def reply(self, message):
        """Sends a message as a reply to this message instance.
        
        Although Django's e-mail processing will set both Message-ID
        and Date upon generating the e-mail message, we will not be able
        to retrieve that information through normal channels, so we must
        pre-set it.

        """
        if self.mailbox.from_email:
            message.from_email = self.mailbox.from_email
        else:
            message.from_email = settings.DEFAULT_FROM_EMAIL
        message.extra_headers['Message-ID'] = make_msgid()
        message.extra_headers['Date'] = formatdate()
        message.extra_headers['In-Reply-To'] = self.message_id
        message.send()
        return self.mailbox.record_outgoing_message(
                email.message_from_string(
                    message.message().as_string()
                )
            )

    def get_email_object(self):
        return email.message_from_string(self.body)

    def __unicode__(self):
        return self.subject
