Introduction
~~~~~~~~~~~~

How many times have you had to consume some sort of POP3 or IMAP mailbox for incoming content?  One too many times for me.

This small Django application will allow you to specify IMAP or POP3 mailboxes that you would like consumed for incoming content; the e-mail will be stored, and you can process it at will (or, if you're in a hurry, by subscribing to a signal).

WARNING!  This app will delete any messages it can find in the inbox you specify-- please make sure you don't have anything important in there.

URI Examples
============

Mailbox URIs are in the normal URI format::

    protocol://username:password@domain

IMAP Example: ``imap://username:password@server``

POP3 Example: ``pop3://username:password@server``

Subscribing to the incoming mail signal
=======================================

To subscribe to the incoming mail signal, following this lead::

    from django_mailbox.signals import message_received
    from django.dispatch import receiver

    @receiver(message_received)
    def dance_jig(sender, message, **args):
        print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )

Getting incoming mail
=======================

In your code
------------

Mailbox instances have a method named ``get_new_mail``; this method will gather new messages from the server.

Using the Django Admin
----------------------

Check the box next to each of the mailboxes you'd like to fetch e-mail from, and select the 'Get new mail' option.

Using a cron job
----------------

You can easily consume incoming mail by running the management command named ``getmail`` (optionally with an argument of the name of the mailbox you'd like to get the mail for).::

    python manage.py getmail

Settings
========

You can disable mailbox information from being listed in the Django admin by adding a setting named ``DJANGO_MAILBOX_ADMIN_ENABLED`` indicating your preference toward whether or not the models appear in the admin (defaulting to ``True``).
