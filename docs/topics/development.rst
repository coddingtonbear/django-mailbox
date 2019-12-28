Development
===========

Here we describe the development process overview. It's in F.A.Q. format to
make it simple.


How to file a ticket?
---------------------

Just go to https://github.com/coddingtonbear/django-mailbox and create new
one.


How do I get involved?
----------------------

It's simple! If you want to fix a bug, extend documentation or whatever you
think is appropriate for the project and involves changes, just fork the
project on github (https://github.com/coddingtonbear/django-mailbox), create a
separate branch, hack on it, publish changes at your fork and create a pull
request.


Why my issue/pull request was closed?
-------------------------------------

We usually put an explonation while we close issue or PR. It might be for
various reasons, i.e. there were no reply for over a month after our last
comment, there were no tests for the changes etc.


How to do a new release?
----------------------------

To enroll a new release you should perform the following task:

* Ensure the file ``CHANGELOG.rst`` reflects all important changes.
* Ensure the file ``CHANGELOG.rst`` includes a new version identifier and current release date.
* Execute ``bumpversion patch`` (or accordingly - see `Semantic Versioning 2.0 <http://semver.org/>`_ ) to reflect changes in codebase.
* Commit changes to the codebase, e.g. ``git commit -m "Release 1.4.8" -a``.
* Tag a new release, e.g. ``git tag "1.4.8"``.
* Push new tag to repo - ``git push origin --tags``.
* Push a new release to PyPI - ``python setup.py sdist bdist_wheel upload``.

How to add support for a new Django version?
------------------------------------------

Changes are only necessary for new minor or major Django versions.

To add support for a new version perform the following task:

* Ensure that ``tox.ini`` file reflects support for new Django release.
* Verify in tox that the code is executed correctly on all versions of the Python interpreter.
* Ensure that ``.travis.yml`` file reflects support for new Django release. Note the excluded versions of the Python interpreter.
* Verify by pushing changes on a separate branch to see if the changes in TravisCI are correct.
* Proceed to the standard procedure for a new package release (see `How to do a new release?`_ ).
