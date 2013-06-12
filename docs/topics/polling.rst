
Getting incoming mail
=====================

If you are utilizing one of the polling methods above, 
you will need to periodically poll the mailbox for messages using one of the below methods.  
If you are receiving mail directly from a mailserver via a pipe 
-- using the ``processincomingmessage`` management command -- 
you need not concern yourself with this section.

In your code
------------

Mailbox instances have a method named ``get_new_mail``; 
this method will gather new messages from the server.

Using the Django Admin
----------------------

Check the box next to each of the mailboxes you'd like to fetch e-mail from, 
and select the 'Get new mail' option.

Using a cron job
----------------

You can easily consume incoming mail by running the management command named ``getmail`` 
(optionally with an argument of the name of the mailbox you'd like to get the mail for).::

    python manage.py getmail


.. _receiving-mail-from-exim4-or-postfix:

Receiving mail directly from Exim4 or Postfix via a pipe
--------------------------------------------------------

Django Mailbox's ``processincomingmessage`` management command accepts, via ``stdin``, incoming messages.  
You can configure Postfix or Exim4 to pipe incoming mail to this management command 
to import messages directly without polling.  

You need not configure mailbox settings when piping-in messages, 
mailbox entries will be automatically created matching the e-mail address to which incoming messages are sent, 
but if you would like to specify the mailbox name, 
you may provide a single argument to the ``processincmingmessage`` command 
specifying the name of the mailbox you would like it to use (and, if neccessary, create).

Receiving Mail from Exim4
.........................

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
...........................

Although I have not personally tried using Postfix for this, 
Postfix is capable of delivering new mail to a script using ``pipe``. 
Please consult the `Postfix documentation for pipe here <http://www.postfix.org/pipe.8.html>`_.  
You may want to consult the above Exim4 configuration for tips.

