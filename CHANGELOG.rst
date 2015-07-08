Changelog
=========

4.4
---

* Adds Django 1.8 support.

4.3
---

* Adds functionality for allowing one to store the message body on-disk
  instead of in the database.

4.2
---

* Adds 'envelope headers' to the Admin interface.

4.1
---

* Adds Django 1.7 migrations support.

4.0
---

* Adds ``html`` property returning the HTML contents of 
  ``django_mailbox.models.Message`` instances.
  Thanks `@ariel17 <https://github.com/ariel17>`_!
* Adds translation support.
  Thanks `@ariel17 <https://github.com/ariel17>`_!
* **Drops support for Python 3.2**.  The fact that only versions of
  Python newer than 3.2 allow unicode literals has convinced me
  that supporting Python 3.2 is probably more trouble than it's worth.
  Please let me know if you were using Python 3.2, and I've left you
  out in the cold; I'm willing to fix Python 3.2 support if it is
  actively used.

3.4
---

* Adds ``gmail`` transport allowing one to use Google
  OAuth credentials for gathering messages from gmail.
  Thanks `@alexlovelltroy <https://github.com/alexlovelltroy>`_!

3.3
---

* Adds functionality to ``imap`` transport allowing one to
  archive processed e-mails.
  Thanks `@yellowcap <https://github.com/yellowcap>`_!

3.2
---

* Fixes `#13 <https://github.com/coddingtonbear/django-mailbox/issues/13>`_;
  Python 3 support had been broken for some time.  Thanks for catching that,
  `@greendee <https://github.com/greendee>`_!

3.1
---

* Fixes a wide variety of unicode-related errors.

3.0
---

* Restructures message storage such that non-text message attachments
  are stored as files, rather than in the database in their original
  (probably base64-encoded) blobs.
* So many new tests.
