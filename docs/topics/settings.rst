
Settings
========

* ``DJANGO_MAILBOX_ADMIN_ENABLED``
    * Default: ``True``
    * Type: ``boolean``
    * Controls whether mailboxes appear in the Django Admin.
* ``DJANGO_MAILBOX_SKIPPED_EXTENSIONS``
    * Default: ``['.p7s']``
    * Type: ``list``
    * A list of extensions to skip when processing e-mail message attachments.
* ``DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES``
    * Default: ``False``
    * Type: ``boolean``
    * Controls whether or not we remove mimetypes not specified in ``DJANGO_MAILBOX_PRESERVED_MIMETYPES``.
* ``DJANGO_MAILBOX_ALLOWED_MIMETYPES``
    * Default ``['text/html', 'text/plain']``
    * Type: ``list``
    * A list of mimetypes that will remain and be stored in the message payload of the message object.  Has no effect unless ``DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES`` is set to ``True``.

