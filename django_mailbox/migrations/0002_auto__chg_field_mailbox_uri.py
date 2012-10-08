# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Mailbox.uri'
        db.alter_column('django_mailbox_mailbox', 'uri', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Mailbox.uri'
        raise RuntimeError("Cannot reverse this migration. 'Mailbox.uri' and its values cannot be restored.")

    models = {
        'django_mailbox.mailbox': {
            'Meta': {'object_name': 'Mailbox'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'django_mailbox.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailbox': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['django_mailbox.Mailbox']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'received': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['django_mailbox']