from distutils.version import LooseVersion
from unittest import mock

from django.core.management import call_command, CommandError
from django.test import TestCase
import django


class CommandsTestCase(TestCase):
    def test_processincomingmessage_no_args(self):
        """Check that processincomingmessage works with no args"""

        mailbox_name = None
        # Mock handle so that the test doesn't hang waiting for input. Note that we are only testing
        # the argument parsing here -- functionality should be tested elsewhere
        with mock.patch(
            "django_mailbox2.management.commands.processincomingmessage.Command.handle"
        ) as handle:
            # Don't care about the return value
            handle.return_value = None

            call_command("processincomingmessage")
            args, kwargs = handle.call_args

            # Make sure that we called with the right arguments
            try:
                self.assertEqual(kwargs["mailbox_name"], mailbox_name)
            except KeyError:
                # Handle Django 1.7
                # It uses optparse instead of argparse, so instead of being
                # set to None, mailbox_name is simply left out altogether
                # Thus we expect an empty tuple here
                self.assertEqual(args, tuple())

    def test_processincomingmessage_with_arg(self):
        """Check that processincomingmessage works with mailbox_name given"""

        mailbox_name = "foo_mailbox"

        with mock.patch(
            "django_mailbox2.management.commands.processincomingmessage.Command.handle"
        ) as handle:
            handle.return_value = None

            call_command("processincomingmessage", mailbox_name)
            args, kwargs = handle.call_args
            try:
                self.assertEqual(kwargs["mailbox_name"], mailbox_name)
            except (AssertionError, KeyError):
                # Handle Django 1.7
                # It uses optparse instead of argparse, so instead of being
                # in kwargs, mailbox_name is in args
                self.assertEqual(args[0], mailbox_name)

    def test_processincomingmessage_too_many_args(self):
        """Check that processincomingmessage raises an error if too many args"""
        # Only perform this test for Django versions greater than 1.7.*. This
        # is because, with optparse, too many arguments doesn't result in an
        # error, which means this test is worthless anyway
        # For the "compatibility" versions, unexpected arguments aren't handled
        # very well, and result in a TypeError
        if LooseVersion(django.get_version()) >= LooseVersion("1.8") and LooseVersion(
            django.get_version()
        ) < LooseVersion("1.10"):
            with self.assertRaises(TypeError):
                call_command("processincomingmessage", "foo_mailbox", "invalid_arg")
        # In 1.10 and later a proper CommandError should be raised
        elif LooseVersion(django.get_version()) >= LooseVersion("1.10"):
            with self.assertRaises(CommandError):
                call_command("processincomingmessage", "foo_mailbox", "invalid_arg")
