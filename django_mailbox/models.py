import base64
import email
from email.header import decode_header
from email.message import Message as EmailMessage
from email.utils import formatdate, parseaddr
from email.encoders import encode_base64
import urllib
import mimetypes
import os.path
from quopri import encode as encode_quopri
import sys
import uuid

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from django.conf import settings
from django.core.mail.message import make_msgid
from django.core.files.base import ContentFile
from django.db import models
from django_mailbox.transports import Pop3Transport, ImapTransport,\
    MaildirTransport, MboxTransport, BabylTransport, MHTransport, \
    MMDFTransport
from django_mailbox.signals import message_received
import six


STRIP_UNALLOWED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES',
    False
)
ALLOWED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_ALLOWED_MIMETYPES',
    [
        'text/plain',
        'text/html'
    ]
)
TEXT_STORED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_TEXT_STORED_MIMETYPES',
    [
        'text/plain',
        'text/html'
    ]
)
ALTERED_MESSAGE_HEADER = getattr(
    settings,
    'DJANGO_MAILBOX_ALTERED_MESSAGE_HEADER',
    'X-Django-Mailbox-Altered-Message'
)
ATTACHMENT_INTERPOLATION_HEADER = getattr(
    settings,
    'DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER',
    'X-Django-Mailbox-Interpolate-Attachment'
)


class ActiveMailboxManager(models.Manager):
    def get_query_set(self):
        return super(ActiveMailboxManager, self).get_query_set().filter(
            active=True,
        )


class Mailbox(models.Model):
    name = models.CharField(max_length=255)
    uri = models.CharField(
        max_length=255,
        help_text=(
            "Example: imap+ssl://myusername:mypassword@someserver <br />"
            "<br />"
            "Internet transports include 'imap' and 'pop3'; "
            "common local file transports include 'maildir', 'mbox', "
            "and less commonly 'babyl', 'mh', and 'mmdf'. <br />"
            "<br />"
            "Be sure to urlencode your username and password should they "
            "contain illegal characters (like @, :, etc)."
        ),
        blank=True,
        null=True,
        default=None,
    )
    from_email = models.CharField(
        max_length=255,
        help_text=(
            "Example: MailBot &lt;mailbot@yourdomain.com&gt;<br />"
            "'From' header to set for outgoing email.<br />"
            "<br />"
            "If you do not use this e-mail inbox for outgoing mail, this "
            "setting is unnecessary.<br />"
            "If you send e-mail without setting this, your 'From' header will'"
            "be set to match the setting `DEFAULT_FROM_EMAIL`."
        ),
        blank=True,
        null=True,
        default=None,
    )
    active = models.BooleanField(
        help_text=(
            "Check this e-mail inbox for new e-mail messages during polling "
            "cycles.  This checkbox does not have an effect upon whether "
            "mail is collected here when this mailbox receives mail from a "
            "pipe, and does not affect whether e-mail messages can be "
            "dispatched from this mailbox. "
        ),
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

    def _get_dehydrated_message(self, msg, record):
        new = EmailMessage()
        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._get_dehydrated_message(part, record)
                )
        elif (
            STRIP_UNALLOWED_MIMETYPES
            and not msg.get_content_type() in ALLOWED_MIMETYPES
        ):
            for header, value in msg.items():
                new[header] = value
            # Delete header, otherwise when attempting to  deserialize the
            # payload, it will be expecting a body for this.
            del new['Content-Transfer-Encoding']
            new[ALTERED_MESSAGE_HEADER] = (
                'Stripped; Content type %s not allowed' % (
                    msg.get_content_type()
                )
            )
            new.set_payload('')
        elif msg.get_content_type() not in TEXT_STORED_MIMETYPES:
            filename = msg.get_filename()
            if not filename:
                extension = mimetypes.guess_extension(msg.get_content_type())
            else:
                _, extension = os.path.splitext(filename)
            if not extension:
                extension = '.bin'

            attachment = MessageAttachment()

            attachment.document.save(
                uuid.uuid4().hex + extension,
                ContentFile(
                    six.BytesIO(
                        msg.get_payload(decode=True)
                    ).getvalue()
                )
            )
            attachment.message = record
            for key, value in msg.items():
                attachment[key] = value
            attachment.save()

            placeholder = EmailMessage()
            placeholder[ATTACHMENT_INTERPOLATION_HEADER] = str(attachment.pk)
            new = placeholder
        else:
            new = msg
        return new

    def _process_message(self, message):
        msg = Message()
        msg.mailbox = self
        if 'subject' in message:
            msg.subject = message['subject'][0:255]
        if 'message-id' in message:
            msg.message_id = message['message-id'][0:255]
        if 'from' in message:
            msg.from_header = message['from']
        if 'to' in message:
            msg.to_header = message['to']
        msg.save()
        message = self._get_dehydrated_message(message, msg)
        msg.set_body(message.as_string())
        if message['in-reply-to']:
            try:
                msg.in_reply_to = Message.objects.filter(
                    message_id=message['in-reply-to']
                )[0]
            except IndexError:
                pass
        msg.save()
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
    encoded = models.BooleanField(
        default=False,
        help_text='True if the e-mail body is Base64 encoded'
    )

    processed = models.DateTimeField(
        auto_now_add=True
    )
    read = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
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
        addresses = []
        addresses = self.to_addresses + self.from_address
        return addresses

    @property
    def from_address(self):
        if self.from_header:
            return [parseaddr(self.from_header)[1].lower()]
        else:
            return []

    @property
    def to_addresses(self):
        addresses = []
        for address in self.to_header.split(','):
            if address:
                addresses.append(
                    parseaddr(
                        address
                    )[1].lower()
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

    @property
    def text(self):
        return self.get_text_body()

    def get_text_body(self):
        def get_body_from_message(message):
            body = ''
            for part in message.walk():
                if (
                    part.get_content_maintype() == 'text'
                    and part.get_content_subtype() == 'plain'
                ):
                    charset = part.get_content_charset()
                    this_part = part.get_payload(decode=True)
                    if charset:
                        this_part = this_part.decode(charset, 'replace')

                    body += this_part
            return body

        return get_body_from_message(
            self.get_email_object()
        ).replace('=\n', '').strip()

    def _rehydrate(self, msg):
        new = EmailMessage()
        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._rehydrate(part)
                )
        elif ATTACHMENT_INTERPOLATION_HEADER in msg.keys():
            try:
                attachment = MessageAttachment.objects.get(
                    pk=msg[ATTACHMENT_INTERPOLATION_HEADER]
                )
                for header, value in attachment.items():
                    new[header] = value
                encoding = new['Content-Transfer-Encoding']
                if encoding and encoding.lower() == 'quoted-printable':
                    # Cannot use `email.encoders.encode_quopri due to
                    # bug 14360: http://bugs.python.org/issue14360
                    output = six.BytesIO()
                    encode_quopri(
                        six.BytesIO(
                            attachment.document.read()
                        ),
                        output,
                        quotetabs=True,
                        header=False,
                    )
                    new.set_payload(
                        output.getvalue().decode().replace(' ', '=20')
                    )
                    del new['Content-Transfer-Encoding']
                    new['Content-Transfer-Encoding'] = 'quoted-printable'
                else:
                    new.set_payload(
                        attachment.document.read()
                    )
                    del new['Content-Transfer-Encoding']
                    encode_base64(new)
            except MessageAttachment.DoesNotExist:
                new[ALTERED_MESSAGE_HEADER] = (
                    'Missing; Attachment %s not found' % (
                        msg[ATTACHMENT_INTERPOLATION_HEADER]
                    )
                )
                new.set_payload('')
        else:
            for header, value in msg.items():
                new[header] = value
            new.set_payload(
                msg.get_payload()
            )
        return new

    def get_body(self):
        if self.encoded:
            return base64.b64decode(self.body.encode('ascii'))
        return self.body.encode('utf-8')

    def set_body(self, body):
        if sys.version_info >= (3, 0):
            body = body.encode('utf-8')
        self.encoded = True
        self.body = base64.b64encode(body).decode('ascii')

    def get_email_object(self):
        """ Returns an `email.message.Message` instance for this message."""
        body = self.get_body()
        if sys.version_info < (3, 0):
            flat = email.message_from_string(body)
        else:
            flat = email.message_from_bytes(body)
        return self._rehydrate(flat)

    def delete(self, *args, **kwargs):
        for attachment in self.attachments.all():
            # This attachment is attached only to this message.
            attachment.delete()
        return super(Message, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.subject


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='attachments',
        null=True,
        blank=True,
    )
    headers = models.TextField(null=True, blank=True)
    document = models.FileField(upload_to='mailbox_attachments/%Y/%m/%d/')

    def delete(self, *args, **kwargs):
        self.document.delete()
        return super(MessageAttachment, self).delete(*args, **kwargs)

    def _get_rehydrated_headers(self):
        headers = self.headers
        if headers is None:
            return EmailMessage()
        if sys.version_info < (3, 0):
            headers = headers.encode('utf-8')
        return email.message_from_string(headers)

    def _set_dehydrated_headers(self, email_object):
        self.headers = email_object.as_string()

    def __delitem__(self, name):
        rehydrated = self._get_rehydrated_headers()
        del rehydrated[name]
        self._set_dehydrated_headers(rehydrated)

    def __setitem__(self, name, value):
        rehydrated = self._get_rehydrated_headers()
        rehydrated[name] = value
        self._set_dehydrated_headers(rehydrated)

    def get_filename(self):
        file_name = self._get_rehydrated_headers().get_filename()
        if file_name:
            encoded_subject, encoding = decode_header(file_name)[0]
            if encoding:
                encoded_subject = encoded_subject.decode(encoding)
            return encoded_subject
        else:
            return None

    def items(self):
        return self._get_rehydrated_headers().items()

    def __getitem__(self, name):
        value = self._get_rehydrated_headers()[name]
        if value is None:
            raise KeyError('Header %s does not exist' % name)
        return value

    def __unicode__(self):
        return self.document.url
