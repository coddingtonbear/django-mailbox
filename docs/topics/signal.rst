
Subscribing to the incoming mail signal
=======================================

To subscribe to the incoming mail signal, following this lead::

    from django_mailbox.signals import message_received
    from django.dispatch import receiver

    @receiver(message_received)
    def dance_jig(sender, message, **args):
        print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )

.. warning::

   `As with all django signals <https://docs.djangoproject.com/en/dev/topics/signals/>`_,
   this should be loaded either in an app's ``models.py``
   or somewhere else loaded early on.
   If you do not load it early enough, the signal may be fired before your
   signal handler's registration is processed!

