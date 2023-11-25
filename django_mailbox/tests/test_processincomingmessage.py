from unittest import mock

from django.core.management import call_command, CommandError
from django.test import TestCase


class CommandsTestCase(TestCase):
    def test_processincomingmessage_no_args(self):
        """Check that processincomingmessage works with no args"""

        mailbox_name = None
        # Mock handle so that the test doesn't hang waiting for input. Note that we are only testing
        # the argument parsing here -- functionality should be tested elsewhere
        with mock.patch('django_mailbox.management.commands.processincomingmessage.Command.handle') as handle:
            # Don't care about the return value
            handle.return_value = None

            call_command('processincomingmessage')
            args, kwargs = handle.call_args

            # Make sure that we called with the right arguments
            self.assertEqual(kwargs['mailbox_name'], mailbox_name)

    def test_processincomingmessage_with_arg(self):
        """Check that processincomingmessage works with mailbox_name given"""

        mailbox_name = 'foo_mailbox'

        with mock.patch('django_mailbox.management.commands.processincomingmessage.Command.handle') as handle:
            handle.return_value = None

            call_command('processincomingmessage', mailbox_name)
            args, kwargs = handle.call_args

            self.assertEqual(kwargs['mailbox_name'], mailbox_name)

    def test_processincomingmessage_too_many_args(self):
        """Check that processincomingmessage raises an error if too many args"""

        with self.assertRaises(CommandError):
            call_command('processincomingmessage', 'foo_mailbox', 'invalid_arg')
