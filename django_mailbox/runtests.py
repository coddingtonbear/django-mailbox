#!/usr/bin/env python
import sys

from os.path import dirname, abspath

try:
    from django import setup
except ImportError:
    pass
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            },
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django_mailbox',
        ]
    )

from django.test.simple import DjangoTestSuiteRunner


def runtests(*test_args):
    if not test_args:
        test_args = ['django_mailbox']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    try:
        # ensure that AppRegistry has loaded
        setup()
    except NameError:
        # This version of Django is too old for an app registry.
        pass
    runner = DjangoTestSuiteRunner(
        verbosity=1,
        interactive=False,
        failfast=False
    )
    failures = runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
