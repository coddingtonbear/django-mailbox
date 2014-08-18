.. django-mailbox documentation master file, created by
   sphinx-quickstart on Tue Jan 22 20:29:12 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django-mailbox
==============

.. image:: https://travis-ci.org/coddingtonbear/django-mailbox.png?branch=master
   :target: https://travis-ci.org/coddingtonbear/django-mailbox

How many times have you had to consume some sort of POP3, IMAP, or local mailbox for incoming content, 
or had to otherwise construct an application driven by e-mail?
One too many times, I'm sure.

This small Django application will allow you to specify mailboxes that you would like consumed for incoming content; 
the e-mail will be stored, and you can process it at will (or, if you're in a hurry, by subscribing to a signal).

Contents:

.. toctree::
   :maxdepth: 3

   topics/installation
   topics/mailbox_types
   topics/polling
   topics/signal
   topics/appendix


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

