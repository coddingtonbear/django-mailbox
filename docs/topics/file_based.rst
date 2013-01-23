
Local File-based Mailboxes
--------------------------

If you happen to want to consume a file-based mailbox like an Maildir, Mbox, Babyl, MH, or MMDF mailbox, 
you can use this too by entering the appropriate 'protocol' in the URI.  
If you had a maildir, for example, at ``/var/mail/``, you would enter a URI like::

    maildir:///var/mail

Note that there is an additional ``/`` in the above URI after the protocol; 
this is important.

