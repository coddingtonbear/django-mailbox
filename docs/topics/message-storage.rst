
Message Storage Details
=======================

First, it may be helpful to know a little bit about how e-mail messages
are actually sent across the wire:

.. code-block:: http
  
   MIME-Version: 1.0
   Received: by 10.221.0.211 with HTTP; Sun, 20 Jan 2013 12:07:07 -0800 (PST)
   X-Originating-IP: [24.22.122.177]
   Date: Sun, 20 Jan 2013 12:07:07 -0800
   Delivered-To: test@adamcoddington.net
   Message-ID: <CAMdmm+jYCgrxrekAxszmDnBjAytcBym-Ec+uM-+HEtzuKy=M_g@mail.gmail.com>
   Subject: Message With Attachment
   From: Adam Coddington <test@adamcoddington.net>
   To: Adam Coddington <test@adamcoddington.net>
   Content-Type: multipart/mixed; boundary=047d7b33dd729737fe04d3bde348
   
   --047d7b33dd729737fe04d3bde348
   Content-Type: text/plain; charset=UTF-8
   
   This message has an attachment.
   
   --047d7b33dd729737fe04d3bde348
   Content-Type: image/png; name="heart.png"
   Content-Disposition: attachment; filename="heart.png"
   Content-Transfer-Encoding: base64
   X-Attachment-Id: f_hc6mair60
   
   iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAFoTx1HAAAAzUlEQVQoz32RWxXDIBBEr4NIQEIl
   ICESkFAJkRAJSIgEpEQCEqYfu6QUkn7sCcyDGQiSACKSKCAkGwBJwhDwZQNMEiYAIBdQvk7rfaHf
   AO8NBJwCxTGhtFgTHVNaNaJeWFu44AXEHzKCktc7zZ0vss+bMoHSiM2b9mQoX1eZCgGqnWskY3gi
   XXAAxb8BqFiUgBNY7k49Tu/kV7UKPsefrjEOT9GmghYzrk9V03pjDGYKj3d0c06dKZkpTboRaD9o
   B+1m2m81d2Az948xzgdjLaFe95e83AAAAABJRU5ErkJggg==
   
   --047d7b33dd729737fe04d3bde348--

Messages are grouped into multiple message payload parts, and should binary
attachments exist, they are encoded into text using, generally, ``base64`` or
``quoted-printable`` encodings.

Earlier versions of this library would preserve the above text verbatim in the
database, but neither of the above encodings are very efficient methods of
storing binary data, and databases aren't really ideal for storing large
chunks of binary data anyway.

Modern versions of this library (>=2.1) will walk through the original message,
write ``models.MessageAttachment`` records for each non-text attachment,
and alter the message body removing the original payload component, but writing
a custom header providing the library enough information to re-build the
message in the event that one needs a python ``email.message.Message`` object.

.. code-block:: http

   MIME-Version: 1.0
   Received: by 10.221.0.211 with HTTP; Sun, 20 Jan 2013 12:07:07 -0800 (PST)
   X-Originating-IP: [24.22.122.177]
   Date: Sun, 20 Jan 2013 12:07:07 -0800
   Delivered-To: test@adamcoddington.net
   Message-ID: <CAMdmm+jYCgrxrekAxszmDnBjAytcBym-Ec+uM-+HEtzuKy=M_g@mail.gmail.com>
   Subject: Message With Attachment
   From: Adam Coddington <test@adamcoddington.net>
   To: Adam Coddington <test@adamcoddington.net>
   Content-Type: multipart/mixed; boundary=047d7b33dd729737fe04d3bde348
   
   --047d7b33dd729737fe04d3bde348
   Content-Type: text/plain; charset=UTF-8
   
   This message has an attachment.
   
   --047d7b33dd729737fe04d3bde348
   X-Django-Mailbox-Interpolate-Attachment: 1308

   
   --047d7b33dd729737fe04d3bde348--

The above payload is what would continue to be stored in the database.
Although in this constructed example, this reduces the message's size only
marginally, in most instances, attached files are much larger than the
attachment shown here.

.. note::

   Email message bodies are ``base-64`` encoded when stored in the database.

Although the attachment is no longer preserved in the message body above,
and only the ``X-Django-Mailbox-Interpolate-Attachment: 1308`` header remains
in the place of the original attachment, the attachment was stored in a
``django_mailbox.MesageAttachment`` record:

.. list-table::
   :header-rows: 1

   * - Field
     - Value
     - Description
   * - Primary Key
     - ``1308``
     - Uniquely generated for each attachment.
   * - Headers
     - ``Content-Type: image/png; name="heart.png"
       Content-Disposition: attachment; filename="heart.png"
       Content-Transfer-Encoding: base64
       X-Attachment-Id: f_hc6mair60``
     - Raw headers from the actual message's payload part.
   * - File
     - ``(binary file object)``
     - References a stored-on-disk binary file corresponding with this
       attachment.

And were one to run the ``django_mailbox.Message`` instance's 
``get_email_object`` method, the following message will be returned:

.. code-block:: http
  
   MIME-Version: 1.0
   Received: by 10.221.0.211 with HTTP; Sun, 20 Jan 2013 12:07:07 -0800 (PST)
   X-Originating-IP: [24.22.122.177]
   Date: Sun, 20 Jan 2013 12:07:07 -0800
   Delivered-To: test@adamcoddington.net
   Message-ID: <CAMdmm+jYCgrxrekAxszmDnBjAytcBym-Ec+uM-+HEtzuKy=M_g@mail.gmail.com>
   Subject: Message With Attachment
   From: Adam Coddington <test@adamcoddington.net>
   To: Adam Coddington <test@adamcoddington.net>
   Content-Type: multipart/mixed; boundary=047d7b33dd729737fe04d3bde348
   
   --047d7b33dd729737fe04d3bde348
   Content-Type: text/plain; charset=UTF-8
   
   This message has an attachment.
   
   --047d7b33dd729737fe04d3bde348
   Content-Type: image/png; name="heart.png"
   Content-Disposition: attachment; filename="heart.png"
   X-Attachment-Id: f_hc6mair60
   Content-Transfer-Encoding: base64
   
   iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAFoTx1HAAAAzUlEQVQoz32RWxXDIBBEr4NIQEIl
   ICESkFAJkRAJSIgEpEQCEqYfu6QUkn7sCcyDGQiSACKSKCAkGwBJwhDwZQNMEiYAIBdQvk7rfaHf
   AO8NBJwCxTGhtFgTHVNaNaJeWFu44AXEHzKCktc7zZ0vss+bMoHSiM2b9mQoX1eZCgGqnWskY3gi
   XXAAxb8BqFiUgBNY7k49Tu/kV7UKPsefrjEOT9GmghYzrk9V03pjDGYKj3d0c06dKZkpTboRaD9o
   B+1m2m81d2Az948xzgdjLaFe95e83AAAAABJRU5ErkJggg==
   
   --047d7b33dd729737fe04d3bde348--

.. note::

   Note that although the above is functionally identical to the originally
   received message, there were changes in the order of headers in rehydrated
   message components, and whitespace changes are also possible (but not
   shown above).
