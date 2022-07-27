from django.dispatch.dispatcher import Signal

message_received = Signal(providing_args=['message'])
