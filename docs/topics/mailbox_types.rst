
Supported Mailbox Types
=======================

Django Mailbox supports polling both common internet mailboxes like
POP3 and IMAP as well as local file-based mailboxes.

.. table:: 'Protocol' Options

  ============ ============== =================================================================================================================================================================
  Mailbox Type 'Protocol'://  Notes
  ============ ============== =================================================================================================================================================================
  POP3         ``pop3://``    Can also specify SSL with ``pop3+ssl://``
  IMAP         ``imap://``    Can also specify SSL with ``imap+ssl://``, or specify a folder to save processed messages into by appending ``?archive=my_archive_folder`` to the end of the URI.
  Maildir      ``maildir://``
  Mbox         ``mbox://``
  Babyl        ``babyl://``
  MH           ``mh://``
  MMDF         ``mmdf://``
  Piped Mail   *empty*        See :ref:`receiving-mail-from-exim4-or-postfix`
  ============ ============== =================================================================================================================================================================


.. warning::

   Unless you are using IMAP's 'Archive' feature,
   this will delete any messages it can find in the inbox you specify;
   do not use an e-mail inbox that you would like to share between
   applications.


POP3 and IMAP Mailboxes
-----------------------

Mailbox URIs are in the normal URI format::

    protocol://username:password@domain

Basic IMAP Example: ``imap://username:password@server``

Basic POP3 Example: ``pop3://username:password@server``

Most mailboxes these days are SSL-enabled; 
if yours is, add ``+ssl`` to the protocol section of your URI.  
Also, if your username or password include any non-ascii characters,
they should be URL-encoded  (for example, if your username includes an
``@``, it should be changed to ``%40`` in your URI).

If you are using an IMAP Mailbox, you can archive all messages before they
are deleted from the inbox. To archive emails, add the archive folder
name as a query paremeter to the uri.  For example, if your mailbox has a
folder named ``myarchivefolder`` that you would like to copy messages to
after processing, add ``?archive=myarchivefolder`` to the end of the URI.

For a verbose example, if you have an account named
``youremailaddress@gmail.com`` with a password
of ``1234`` on GMail, which uses a IMAP server of ``imap.gmail.com`` (requiring
SSL) and you would like to archive all processed emails
into a folder named ``Archived``, you
would enter the following as your URI::

    imap+ssl://youremailaddress%40gmail.com:1234@imap.gmail.com?archive=Archived

Gmail IMAP with Oauth2 authentication
-------------------------------------

Gmail supports using oauth2 for authentication_ which is more secure.
To handle the handshake and storing the credentials, use python-social-auth_.

.. _authentication: https://developers.google.com/gmail/xoauth2_protocol
.. _python-social-auth: http://psa.matiasaguirre.net/

The Gmail Mailbox is also a regular IMAP mailbox, but the password will be ignored if oauth2 succeeds.  It can fall back to password as needed.
Build your URI accordingly::

    gmail+ssl://youremailaddress%40gmail.com:oauth2@imap.gmail.com?archive=Archived


Local File-based Mailboxes
--------------------------

If you happen to want to consume a file-based mailbox like an Maildir, Mbox,
Babyl, MH, or MMDF mailbox, you can use this too by entering the appropriate
'protocol' in the URI.  If you had a maildir, for example, at ``/var/mail/``,
you would enter a URI like::

    maildir:///var/mail

Note that there is an additional ``/`` in the above URI after the protocol; 
this is important.

