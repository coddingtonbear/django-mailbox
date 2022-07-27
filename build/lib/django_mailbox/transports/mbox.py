from mailbox import mbox
from django_mailbox.transports.generic import GenericFileMailbox


class MboxTransport(GenericFileMailbox):
    _variant = mbox
