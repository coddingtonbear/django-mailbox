from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MailBoxConfig(AppConfig):
    name = "django_mailbox2"
    verbose_name = _("Mail Box 2")
