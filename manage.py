import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_mailbox.tests.settings'

from django.core import management

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    management.execute_from_command_line()
    sys.exit()