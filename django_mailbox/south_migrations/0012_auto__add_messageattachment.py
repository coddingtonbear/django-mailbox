# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MessageAttachment'
        db.create_table('django_mailbox_messageattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('django_mailbox', ['MessageAttachment'])

        # Adding M2M table for field attachments on 'Message'
        db.create_table('django_mailbox_message_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm['django_mailbox.message'], null=False)),
            ('messageattachment', models.ForeignKey(orm['django_mailbox.messageattachment'], null=False))
        ))
        db.create_unique('django_mailbox_message_attachments', ['message_id', 'messageattachment_id'])


    def backwards(self, orm):
        
        # Deleting model 'MessageAttachment'
        db.delete_table('django_mailbox_messageattachment')

        # Removing M2M table for field attachments on 'Message'
        db.delete_table('django_mailbox_message_attachments')


    models = {
        'django_mailbox.mailbox': {
            'Meta': {'object_name': 'Mailbox'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'from_email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'django_mailbox.message': {
            'Meta': {'object_name': 'Message'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_mailbox.MessageAttachment']", 'symmetrical': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'from_header': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'replies'", 'null': 'True', 'to': "orm['django_mailbox.Message']"}),
            'mailbox': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['django_mailbox.Mailbox']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'outgoing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'read': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_header': ('django.db.models.fields.TextField', [], {})
        },
        'django_mailbox.messageattachment': {
            'Meta': {'object_name': 'MessageAttachment'},
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['django_mailbox']
