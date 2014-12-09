from django.core.mail import get_connection, EmailMultiAlternatives, EmailMessage, make_msgid


def record_messages(mailbox, messages, related_object=None):
    """
    Used in functions below. Records sent messages in Django Mailbox.
    """
    for message in messages:
        mailbox.record_outgoing_message(message.message(), related_object)


def send_mass_mail_recorded(datatuple, mailbox, related_object=None, bcc=None,
                            fail_silently=False, auth_user=None, auth_password=None, connection=None):
    """
    Shadows Django's send mass mail, but records each outgoing message to the
    specified mailbox.

    Also added optional bcc argument.
    """
    connection = connection or get_connection(
        username=auth_user, password=auth_password, fail_silently=fail_silently
    )

    messages = [EmailMessage(subject, message, sender, recipient, bcc, headers={'Message-ID': make_msgid()})
                for subject, message, sender, recipient in datatuple]

    record_messages(mailbox, messages, related_object)

    return connection.send_messages(messages)


def send_mass_html_mail_recorded(datatuple, mailbox, related_object=None, bcc=None,
                                 fail_silently=False, user=None, password=None, connection=None):
    """
    Like above, but lets you send HTML emails.
    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )

    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient, bcc, headers={'Message-ID': make_msgid()})
        message.attach_alternative(html, 'text/html')
        messages.append(message)

    record_messages(mailbox, messages)

    return connection.send_messages(messages)