from mailbox import Babyl
from django_mailbox2.transports.generic import GenericFileMailbox


class BabylTransport(GenericFileMailbox):
    _variant = Babyl
