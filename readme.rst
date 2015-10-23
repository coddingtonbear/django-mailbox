.. image:: https://travis-ci.org/coddingtonbear/django-mailbox.png?branch=master
   :target: https://travis-ci.org/coddingtonbear/django-mailbox

.. image:: https://badge.fury.io/py/django-mailbox.png
    :target: http://badge.fury.io/py/django-mailbox

.. image:: https://pypip.in/d/django-mailbox/badge.png
    :target: https://pypi.python.org/pypi/django-mailbox


Easily ingest messages from POP3, IMAP, or local mailboxes into your Django application.

This app allows you to either ingest e-mail content from common e-mail services (as long as the service provides POP3 or IMAP support),
or directly recieve e-mail messages from ``stdin`` (for locally processing messages from Postfix or Exim4).

These ingested messages will be stored in the database in Django models and you can process their content at will,
or -- if you're in a hurry -- by using a signal receiver.

- Documentation for django-mailbox is available on
  `ReadTheDocs <http://django-mailbox.readthedocs.org/>`_.
- Please post issues on
  `Github <http://github.com/coddingtonbear/django-mailbox/issues>`_.
- Test status available on
  `Travis-CI <https://travis-ci.org/coddingtonbear/django-mailbox>`_.


.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/coddingtonbear/django-mailbox
   :target: https://gitter.im/coddingtonbear/django-mailbox?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge