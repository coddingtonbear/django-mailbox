
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
