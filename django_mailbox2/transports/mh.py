from mailbox import MH
from django_mailbox2.transports.generic import GenericFileMailbox


class MHTransport(GenericFileMailbox):
    _variant = MH
