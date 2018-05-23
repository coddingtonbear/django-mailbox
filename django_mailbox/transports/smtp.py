import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# from django.conf import settings
# from django.core.mail import EmailMessage

from django_mailbox.transports.base import EmailTransport, MessageParseError


class SMTPTransport(EmailTransport):
    def __init__(self,
                 hostname, port=None, ssl=False, tls=False):
        self.hostname = hostname
        self.port = port
        self.tls = tls

        if ssl:
            self.transport = smtplib.SMTP_SSL
            if not self.port:
                self.port = 465
        else:
            self.transport = smtplib.SMTP
            if not self.port:
                self.port = 25

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
        if self.tls:
            self.server.starttls()

        typ, msg = self.server.login(user=username, password=password)

    # TODO Add abilities for html, image sending.
    def send_message(self, subject, message, from_email, recipient_list):
        msg = MIMEMultipart(message)

        msg_text = MIMEText(message, 'plain')

        msg.attach(msg_text)

        msg['From'] = from_email
        msg['To'] = recipient_list
        msg['Subject'] = subject

        self.server.sendmail(msg['From'], msg['To'], msg.as_string())
        self.server.quit()

