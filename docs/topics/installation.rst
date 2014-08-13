
Installation
============

You can either install from pip::

    pip install django-mailbox

*or* checkout and install the source from the `github repository <https://github.com/coddingtonbear/django-mailbox/>`_::

    git clone https://github.com/coddingtonbear/django-mailbox.git
    cd django-mailbox
    python setup.py install

After you have installed the package, 
you should add ``django_mailbox`` to the ``INSTALLED_APPS`` setting in your project's ``settings.py`` file.

Run ``python manage.py migrate django_mailbox`` to create the required database tables.

Head to your admin and create a mailbox to consume (see next docs page).

Test your setup by selecting 'Get new mail' from the action dropdown in the Mailbox change list.
