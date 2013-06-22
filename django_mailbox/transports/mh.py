from mailbox import MH
from django_mailbox.transports.generic import GenericFileMailbox


class MHTransport(GenericFileMailbox):
    _variant = MH
