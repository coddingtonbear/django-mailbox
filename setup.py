from setuptools import find_packages, setup

from django_mailbox import __version__ as version_string


tests_require = [
    'django',
    'mock',
    'unittest2',
]

gmail_oauth2_require = [
    'python-social-auth',
]

office365_oauth2_require = [
    'O365',
]

setup(
    name='django-mailbox',
    version=version_string,
    url='http://github.com/coddingtonbear/django-mailbox/',
    description=(
        'Import mail from POP3, IMAP, local mailboxes or directly from '
        'Postfix or Exim4 into your Django application automatically.'
    ),
    license='MIT',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    extras_require={
        'gmail-oauth2': gmail_oauth2_require,
        'office365-oauth2': office365_oauth2_require
    },
    python_requires=">=3.8",
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Post-Office',
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Communications :: Email :: Post-Office :: POP3',
        'Topic :: Communications :: Email :: Email Clients (MUA)',
    ],
    packages=find_packages(),
    include_package_data=True,
)
