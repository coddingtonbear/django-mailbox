from smtplib import SMTP, SMTP_SSL

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from django_mailbox.transports.base import EmailTransport


class SMTPTransport(EmailTransport):
    def __init__(self, hostname, port=None,
                 ssl=False, tls=False):
        self.hostname = hostname
        self.port = port
        self.tls = tls
        self.server = None

        if ssl:
            self.transport = SMTP_SSL
            if not self.port:
                self.port = 465
        else:
            self.transport = SMTP
            if not self.port:
                self.port = 25

    def connect(self, username, password):
        self.server = self.transport(self.hostname, self.port)
        if self.tls:
            self.server.starttls()

        _ = self.server.login(user=username, password=password)

    def send_message(self, subject, message, from_email, recipient_list, img=None, html=False):
        msg = MIMEMultipart()

        msg_text = MIMEText(message, 'plain' if not html else 'html')

        if img:
            with open(img, 'rb') as fp:
                msg_img = MIMEImage(fp.read())
            msg.attach(msg_img)

        msg.attach(msg_text)

        msg['From'] = from_email
        msg['To'] = recipient_list
        msg['Subject'] = subject

        self.server.sendmail(msg['From'], msg['To'], msg.as_string())
        self.server.quit()
