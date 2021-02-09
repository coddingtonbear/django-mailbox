from mailbox import MMDF
from django_mailbox2.transports.generic import GenericFileMailbox


class MMDFTransport(GenericFileMailbox):
    _variant = MMDF
