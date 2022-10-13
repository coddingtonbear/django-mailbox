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
        'gmail-oauth2': gmail_oauth2_require
    },
    python_requires=">=3",
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Post-Office',
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Communications :: Email :: Post-Office :: POP3',
        'Topic :: Communications :: Email :: Email Clients (MUA)',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'six>=1.6.1',
    ]
)
