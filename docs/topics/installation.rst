
Installation
============

1. You can either install from pip::

       pip install django-mailbox
   
   *or* checkout and install the source from the `github repository <https://github.com/coddingtonbear/django-mailbox/>`_::
   
       git clone https://github.com/coddingtonbear/django-mailbox.git
       cd django-mailbox
       python setup.py install

2. After you have installed the package, 
   add ``django_mailbox`` to the ``INSTALLED_APPS`` setting in
   your project's ``settings.py`` file.

3. From your project folder, run ``python manage.py migrate django_mailbox`` to
   create the required database tables.

4. Head to your project's Django Admin and create a mailbox to consume.


.. note::

   Once you have entered a mailbox to consume, you can easily verify that you
   have properly configured your mailbox by either:

   * From the Django Admin, using the 'Get New Mail' action from the action
     dropdown on the Mailbox changelist 
     (http://yourproject.com/admin/django_mailbox/mailbox/).
   * *Or* from a shell opened to your project's directory, using the
     ``getmail`` management command by running::

       python manage.py getmail

