
Subscribing to the incoming mail signal
=======================================

To subscribe to the incoming mail signal, following this lead::

    from django_mailbox.signals import message_received
    from django.dispatch import receiver

    @receiver(message_received)
    def dance_jig(sender, message, **args):
        print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )

