from setuptools import setup, find_packages

setup(
    name='django_mailbox',
    version='0.1',
    url='http://bitbucket.org/latestrevision/django-mailbox/',
    description='Automatically import mail from POP3 or IMAP into Django',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
)
