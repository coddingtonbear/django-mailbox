
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

