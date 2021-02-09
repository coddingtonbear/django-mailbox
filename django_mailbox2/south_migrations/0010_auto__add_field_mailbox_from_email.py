import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding field 'Mailbox.from_email'
        db.add_column(
            "django_mailbox2_mailbox",
            "from_email",
            self.gf("django.db.models.fields.CharField")(
                default=None, max_length=255, null=True, blank=True
            ),
            keep_default=False,
        )

    def backwards(self, orm):
        # Deleting field 'Mailbox.from_email'
        db.delete_column("django_mailbox2_mailbox", "from_email")

    models = {
        "django_mailbox2.mailbox": {
            "Meta": {"object_name": "Mailbox"},
            "active": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "from_email": (
                "django.db.models.fields.CharField",
                [],
                {
                    "default": "None",
                    "max_length": "255",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": ("django.db.models.fields.CharField", [], {"max_length": "255"}),
            "uri": (
                "django.db.models.fields.CharField",
                [],
                {
                    "default": "None",
                    "max_length": "255",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "django_mailbox2.message": {
            "Meta": {"object_name": "Message"},
            "body": ("django.db.models.fields.TextField", [], {}),
            "from_header": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "in_reply_to": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'replies'",
                    "null": "True",
                    "to": "orm['django_mailbox2.Message']",
                },
            ),
            "mailbox": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'messages'", "to": "orm['django_mailbox2.Mailbox']"},
            ),
            "message_id": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
            ),
            "outgoing": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "processed": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "subject": ("django.db.models.fields.CharField", [], {"max_length": "255"}),
            "to_header": ("django.db.models.fields.TextField", [], {}),
        },
    }

    complete_apps = ["django_mailbox2"]
