Django Mailbox2
===============

This is a modified version of the original.

Easily ingest messages from POP3, IMAP, or local mailboxes into your Django application. 

This is a modified version that has extra features. I think I need to make it better.

This app allows you to either ingest e-mail content from common e-mail services (as long as the service provides POP3 or IMAP support),
or directly receive e-mail messages from ``stdin`` (for locally processing messages from Postfix or Exim4).

These ingested messages will be stored in the database in Django models and you can process their content at will,
or -- if you're in a hurry -- by using a signal receiver.


Usage
-----

1. poetry add django-mailbox

2. After you have installed the package, add django_mailbox to the INSTALLED_APPS setting in your project’s settings.py file.

3. From your project folder, run python manage.py migrate django_mailbox to create the required database tables.

4. Head to your project’s Django Admin and create a mailbox to consume.
  a. if you do not want it to delete the messages on the server add these to settings.py
     set DJANGO_MAILBOX_DELETE_MESSAGE_FROM_SERVER to false
     set DJANGO_MAILBOX_DELETE_MESSAGE_ID_STORE to /path/to/messageid_store.json

5. python manage.py getmail


- Documentation for django-mailbox is available on
  `ReadTheDocs <http://django-mailbox.readthedocs.org/>`_.
- Please post issues on
  `Github <http://github.com/coddingtonbear/django-mailbox/issues>`_.
- Test status available on
  `Travis-CI <https://travis-ci.org/coddingtonbear/django-mailbox>`_.

Development
-----------

export DJANGO_SETTINGS_MODULE=websrv.settings

