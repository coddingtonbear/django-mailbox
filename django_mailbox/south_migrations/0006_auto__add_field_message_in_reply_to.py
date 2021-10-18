import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Message.in_reply_to'
        db.add_column('django_mailbox_message', 'in_reply_to',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='replies', null=True, to=orm['django_mailbox.Message']),
                      keep_default=False)

        # Adding M2M table for field references on 'Message'
        db.create_table('django_mailbox_message_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_message', models.ForeignKey(orm['django_mailbox.message'], null=False)),
            ('to_message', models.ForeignKey(orm['django_mailbox.message'], null=False))
        ))
        db.create_unique('django_mailbox_message_references', ['from_message_id', 'to_message_id'])


    def backwards(self, orm):
        # Deleting field 'Message.in_reply_to'
        db.delete_column('django_mailbox_message', 'in_reply_to_id')

        # Removing M2M table for field references on 'Message'
        db.delete_table('django_mailbox_message_references')


    models = {
        'django_mailbox.mailbox': {
            'Meta': {'object_name': 'Mailbox'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'django_mailbox.message': {
            'Meta': {'object_name': 'Message'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'replies'", 'null': 'True', 'to': "orm['django_mailbox.Message']"}),
            'mailbox': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['django_mailbox.Mailbox']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'outgoing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'referenced_by'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['django_mailbox.Message']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['django_mailbox']