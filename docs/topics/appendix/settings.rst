
Settings
========

* ``DJANGO_MAILBOX_ADMIN_ENABLED``

  * Default: ``True``
  * Type: ``boolean``
  * Controls whether mailboxes appear in the Django Admin.

* ``DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES``

  * Default: ``False``
  * Type: ``boolean``
  * Controls whether or not we remove mimetypes not specified in
    ``DJANGO_MAILBOX_PRESERVED_MIMETYPES`` from the message prior to storage.

* ``DJANGO_MAILBOX_ALLOWED_MIMETYPES``

  * Default ``['text/html', 'text/plain']``
  * Type: ``list``
  * Should ``DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES`` be ``True``, this is
    a list of mimetypes that will not be stripped from the message prior
    to processing attachments.
    Has no effect unless ``DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES``
    is set to ``True``.

* ``DJANGO_MAILBOX_TEXT_STORED_MIMETYPES``

  * Default: ``['text/html', 'text/plain']``
  * Type: ``list``
  * A list of mimetypes that will remain stored in the text body of the
    message in the database.  See :doc:`message-storage`.

* ``DJANGO_MAILBOX_ALTERED_MESSAGE_HEADER``

  * Default: ``X-Django-Mailbox-Altered-Message``
  * Type: ``string``
  * Header to add to a message payload part in the event that the message
    cannot be reproduced accurately. Possible values include:

    * ``Missing``: The message could not be reconstructed because the message
      payload component (stored outside this database record) could not be
      found.  This will be followed by a semicolon (``;``) and a short, more
      detailed description of which record was not found.
    * ``Stripped`` The message could not be reconstructed because the message
      payload component was intentionally stripped from the message body prior
      to storage.  This will be followed by a semicolon (``;``) and a short,
      more detailed description of why this payload component was stripped.

* ``DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER``

  * Default: ``X-Django-Mailbox-Interpolate-Attachment``
  * Type: ``string``
  * Header to add to the temporary 'dehydrated' message body in lieu of
    a non-text message payload component. The value of this header will be used
    to 'rehydrate' the message into a proper e-mail object in the event of
    a message instance's ``get_email_object`` method being called.  Value of
    this field is the primary key of the ``django_mailbox.MessageAttachment``
    instance currently storing this payload component's contents.

* ``DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO``

  * Default: ``mailbox_attachments/%Y/%m/%d/``
  * Type: ``string``
  * Attachments will be saved to this location. Specifies the ``upload_to`` setting
    for the attachment FileField. For more on FileFields and upload_to, see the
    `Django docs <https://docs.djangoproject.com/en/dev/topics/http/file-uploads/#handling-uploaded-files-with-a-model>`__

* ``DJANGO_MAILBOX_MAX_MESSAGE_SIZE``

  * Default: ``False``
  * Type: ``integer``
  * If this is set, it will be read as a number of
    bytes.  Any messages above that size will not be
    downloaded.  ``2000000`` is 2 Megabytes.

* ``DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE``

  * Default: ``False``
  * Type: ``boolean``
  * Controls whether or not we store original messages in ``eml`` field
