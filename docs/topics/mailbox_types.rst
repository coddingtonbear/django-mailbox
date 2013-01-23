
Supported Mailbox Types
=======================

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
