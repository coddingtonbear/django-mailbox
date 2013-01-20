.. image:: https://travis-ci.org/latestrevision/django-mailbox.png?branch=master

How many times have you had to consume some sort of POP3, IMAP, or local mailbox for incoming content, 
or had to otherwise construct an application driven by e-mail?
One too many times, I'm sure.

This small Django application will allow you to specify mailboxes that you would like consumed for incoming content; 
the e-mail will be stored, and you can process it at will (or, if you're in a hurry, by subscribing to a signal).

Installation
============

You can either install from pip::

    pip install django-mailbox

*or* checkout and install the source from the `bitbucket repository <https://bitbucket.org/latestrevision/django-mailbox/>`_::

    hg clone https://bitbucket.org/latestrevision/django-mailbox
    cd django-mailbox
    python setup.py install

*or* checkout and install the source from the `github repository <https://github.com/latestrevision/django-mailbox/>`_::

    git clone https://github.com/latestrevision/django-mailbox.git
    cd django-mailbox
    python setup.py install

After you have installed the package, 
you should add ``django_mailbox`` to the ``INSTALLED_APPS`` setting in your project's ``settings.py`` file.

Polling for mail in POP3/IMAP or a local mailbox
================================================

Django Mailbox supports polling both common internet mailboxes like POP3 and IMAP as well as local file-based mailboxes.

.. table:: 'Protocol' Options

  ============ ============== ===============================================================
  Mailbox Type 'Protocol'://  Notes
  ============ ============== ===============================================================
  POP3         ``pop3://``    Can also specify SSL with ``pop3+ssl://``
  IMAP         ``imap://``    Can also specify SSL with ``imap+ssl://``
  Maildir      ``maildir://``
  Mbox         ``mbox://``
  Babyl        ``babyl://``
  MH           ``mh://``
  MMDF         ``mmdf://``
  Piped Mail   *empty*        See `Receiving mail directly from Exim4 or Postfix via a pipe`_
  ============ ============== ===============================================================

.. WARNING::
   This will delete any messages it can find in the inbox you specify; 
   do not use an e-mail inbox that you would like to share between applications.

POP3 and IMAP Mailboxes
-----------------------

Mailbox URIs are in the normal URI format::

    protocol://username:password@domain

Basic IMAP Example: ``imap://username:password@server``

Basic POP3 Example: ``pop3://username:password@server``

Most mailboxes these days are SSL-enabled; 
if yours is, add ``+ssl`` to your URI.  
Also, if your username or password include any non-ascii characters,  they should be URL-encoded 
(for example, if your username includes an ``@``, it should be changed to ``%40`` in your URI).

If you have an account named ``youremailaddress@gmail.com`` with a password of ``1234`` on GMail,
which uses a POP3 server of 'pop.gmail.com' and requires SSL, 
you would enter the following as your URI::

    pop3+ssl://youremailaddress%40gmail.com:1234@pop.gmail.com

Local File-based Mailboxes
--------------------------

If you happen to want to consume a file-based mailbox like an Maildir, Mbox, Babyl, MH, or MMDF mailbox, 
you can use this too by entering the appropriate 'protocol' in the URI.  
If you had a maildir, for example, at ``/var/mail/``, you would enter a URI like::

    maildir:///var/mail

Note that there is an additional ``/`` in the above URI after the protocol; 
this is important.

Getting incoming mail
---------------------

If you are utilizing one of the polling methods above, 
you will need to periodically poll the mailbox for messages using one of the below methods.  
If you are receiving mail directly from a mailserver via a pipe 
-- using the ``processincomingmessage`` management command -- 
you need not concern yourself with this section.

In your code
............

Mailbox instances have a method named ``get_new_mail``; 
this method will gather new messages from the server.

Using the Django Admin
......................

Check the box next to each of the mailboxes you'd like to fetch e-mail from, 
and select the 'Get new mail' option.

Using a cron job
................

You can easily consume incoming mail by running the management command named ``getmail`` 
(optionally with an argument of the name of the mailbox you'd like to get the mail for).::

    python manage.py getmail

Receiving mail directly from Exim4 or Postfix via a pipe
========================================================

Django Mailbox's ``processincomingmessage`` management command accepts, via ``stdin``, incoming messages.  
You can configure Postfix or Exim4 to pipe incoming mail to this management command 
to import messages directly without polling.  

You need not configure mailbox settings when piping-in messages, 
mailbox entries will be automatically created matching the e-mail address to which incoming messages are sent, 
but if you would like to specify the mailbox name, 
you may provide a single argument to the ``processincmingmessage`` command 
specifying the name of the mailbox you would like it to use (and, if neccessary, create).

Receiving Mail from Exim4
-------------------------

To configure Exim4 to receive incoming mail, 
start by adding a new router configuration to your Exim4 configuration like::

  django_mailbox:
    debug_print = 'R: django_mailbox for $localpart@$domain'
    driver = accept
    domains = +local_domains
    transport = send_to_django_mailbox
    local_parts = emailusernameone : emailusernametwo

Make sure that the e-mail addresses you would like handled by Django Mailbox are not handled by another router; 
you may need to disable some existing routers. 

Change the contents of ``local_parts`` to match a colon-delimited list of usernames for which you would like to receive mail.
For example, if one of the e-mail addresses targeted at this machine is ``jane@example.com``, 
the contents of ``local_parts`` would be, simply ``jane``.

Next, a new transport configuration to your Exim4 configuration::

  send_to_django_mailbox:
    driver = pipe
    command = /path/to/your/environments/python /path/to/your/projects/manage.py processincomingmessage
    user = www-data
    group = www-data
    return_path_add
    delivery_date_add

Like your router configuration, transport configuration should be altered to match your environment.  
First, modify the ``command`` setting such that it points at the proper python executable 
(if you're using a virtual environment, you'll want to direct that at the python executable in your virtual environment) 
and project ``manage.py`` script.  
Additionally, you'll need to set ``user`` and ``group`` such that 
they match a reasonable user and group (on Ubuntu, ``www-data`` suffices for both).

Receiving mail from Postfix
---------------------------

Although I have not personally tried using Postfix for this, 
Postfix is capable of delivering new mail to a script using ``pipe``. 
Please consult the `Postfix documentation for pipe here <http://www.postfix.org/pipe.8.html>`_.  
You may want to consult the above Exim4 configuration for tips.

Subscribing to the incoming mail signal
=======================================

To subscribe to the incoming mail signal, following this lead::

    from django_mailbox.signals import message_received
    from django.dispatch import receiver

    @receiver(message_received)
    def dance_jig(sender, message, **args):
        print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )

Settings
========

You can disable mailbox information from being listed in the Django admin 
by adding a setting named ``DJANGO_MAILBOX_ADMIN_ENABLED`` 
indicating your preference toward whether or not the models appear in the admin 
(defaulting to ``True``).
