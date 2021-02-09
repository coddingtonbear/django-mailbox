import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'Mailbox'
        db.create_table(
            "django_mailbox2_mailbox",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                ("name", self.gf("django.db.models.fields.CharField")(max_length=255)),
                ("uri", self.gf("django.db.models.fields.CharField")(max_length=255)),
            ),
        )
        db.send_create_signal("django_mailbox2", ["Mailbox"])

        # Adding model 'Message'
        db.create_table(
            "django_mailbox2_message",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "mailbox",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["django_mailbox2.Mailbox"]
                    ),
                ),
                (
                    "subject",
                    self.gf("django.db.models.fields.CharField")(max_length=255),
                ),
                (
                    "message_id",
                    self.gf("django.db.models.fields.CharField")(max_length=255),
                ),
                (
                    "from_address",
                    self.gf("django.db.models.fields.CharField")(max_length=255),
                ),
                ("body", self.gf("django.db.models.fields.TextField")()),
                (
                    "received",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("django_mailbox2", ["Message"])

    def backwards(self, orm):
        # Deleting model 'Mailbox'
        db.delete_table("django_mailbox2_mailbox")

        # Deleting model 'Message'
        db.delete_table("django_mailbox2_message")

    models = {
        "django_mailbox2.mailbox": {
            "Meta": {"object_name": "Mailbox"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": ("django.db.models.fields.CharField", [], {"max_length": "255"}),
            "uri": ("django.db.models.fields.CharField", [], {"max_length": "255"}),
        },
        "django_mailbox2.message": {
            "Meta": {"object_name": "Message"},
            "body": ("django.db.models.fields.TextField", [], {}),
            "from_address": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mailbox": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['django_mailbox2.Mailbox']"},
            ),
            "message_id": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
            ),
            "received": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "subject": ("django.db.models.fields.CharField", [], {"max_length": "255"}),
        },
    }

    complete_apps = ["django_mailbox2"]
