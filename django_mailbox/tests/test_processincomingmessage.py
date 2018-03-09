from django.core.management import call_command, CommandError
from django.test import TestCase

import mock

class CommandsTestCase(TestCase):
    def test_processincomingmessage_no_args(self):
        """Check that processincomingmessage works with no args"""
        # Mock handle so that the test doesn't hang waiting for input. Note that we are only testing
        # the argument parsing here -- functionality should be tested elsewhere
        with mock.patch('django_mailbox.management.commands.processincomingmessage.Command.handle') as handle:
            # Don't care about the return value
            handle.return_value = None
            
            call_command('processincomingmessage')
            
            # Define the arguments we expect handle to be called with
            required_arguments = {
                # This should be None, since it isn't given
                'mailbox_name': None,
                # All otheres can be anything; we don't care about them at all
                'no_color': mock.ANY,
                'pythonpath': mock.ANY,
                'settings': mock.ANY,
                'skip_checks': mock.ANY,
                'traceback': mock.ANY,
                'verbosity': mock.ANY
            }
            # Make sure that we called with the right arguments
            handle.assert_called_with(**required_arguments)

    def test_processincomingmessage_with_arg(self):
        """Check that processincomingmessage works with mailbox_name given"""

        with mock.patch('django_mailbox.management.commands.processincomingmessage.Command.handle') as handle:
            handle.return_value = None
            
            call_command('processincomingmessage', 'foo_mailbox')

            required_arguments = {
                'mailbox_name': 'foo_mailbox',
                'no_color': mock.ANY,
                'pythonpath': mock.ANY,
                'settings': mock.ANY,
                'skip_checks': mock.ANY,
                'traceback': mock.ANY,
                'verbosity': mock.ANY
            }
            handle.assert_called_with(**required_arguments)

    def test_processincomingmessage_too_many_args(self):
        """Check that processincomingmessage raises an error if too many args"""
        with self.assertRaises(CommandError):
            call_command('processincomingmessage', 'foo_mailbox', 'invalid_arg')
