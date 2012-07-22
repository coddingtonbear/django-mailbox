Introduction
~~~~~~~~~~~~

How many times have you had to consume some sort of POP3, IMAP, or local mailbox for incoming content?  One too many times for me.

This small Django application will allow you to specify mailboxes that you would like consumed for incoming content; the e-mail will be stored, and you can process it at will (or, if you're in a hurry, by subscribing to a signal).

WARNING!  This will delete any messages it can find in the inbox you specify-- please make sure you don't have anything important in there.

Installation
============

You can either install from pip::

    pip install django-mailbox

*or* checkout and install the source from the [bitbucket repository](https://bitbucket.org/latestrevision/django-mailbox)::

    hg clone https://bitbucket.org/latestrevision/django-mailbox
    cd django-mailbox
    python setup.py install

*or* checkout and install the source from the [github repository](https://github.com/latestrevision/django-mailbox)::

    git clone https://github.com/latestrevision/django-mailbox.git
    cd django-mailbox
    python setup.py install

Setting up your mailbox
=======================

Django Mailbox supports both common internet mailboxes like POP3 and IMAP as well as local file-based mailboxes.

.. table:: 'Protocol' Options

  ============ ============== =========================================
  Mailbox Type 'Protocol'://  Notes
  ============ ============== =========================================
  POP3         ``pop3://``    Can also specify SSL with ``pop3+ssl://``
  IMAP         ``imap://``    Can also specify SSL with ``imap+ssl://``
  Maildir      ``maildir://``
  Mbox         ``mbox://``
  Babyl        ``babyl://``
  MH           ``mh://``
  MMDF         ``mmdf://``
  ============ ============== =========================================

POP3 and IMAP Mailboxes
-----------------------

Mailbox URIs are in the normal URI format::

    protocol://username:password@domain

Basic IMAP Example: ``imap://username:password@server``

Basic POP3 Example: ``pop3://username:password@server``

Most mailboxes these days are SSL-enabled; if yours is, add ``+ssl`` to your URI.  Also, if your username or password include any non-ascii characters,  they should be URL-encoded (for example, if your username includes an ``@``, it should be changed to ``%40`` in your URI).

If you have an account named ``youremailaddress@gmail.com`` with a password of ``1234`` on GMail (which I happen to know uses the POP3 server of 'pop.gmail.com' and requires SSL), you would enter the following as your URI::

    pop3+ssl://youremailaddress%40gmail.com:1234@pop.gmail.com

Local File-based Mailboxes
--------------------------

If you happen to want to consume a file-based mailbox like an Maildir, Mbox, Babyl, MH, or MMDF mailbox, you can use this too by entering the appropriate 'protocol' in the URI.  If you had a maildir, for example, at ``/var/mail/``, you would enter a URI like::

    maildir:///var/mail

Note that there is an additional ``/`` in the above URI after the protocol; this is important.

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
