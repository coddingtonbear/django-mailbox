# -*- coding: utf-8 -*-
import datetime
import email
import hashlib
import logging
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


logger = logging.getLogger(__name__)


class Migration(SchemaMigration):

    def forwards(self, orm):
        ATTACHMENT_HASH_MAP = {}

        attachments_without_messages = orm[
            'django_mailbox.messageattachment'
        ].objects.filter(message=None)

        if attachments_without_messages.count() < 1:
            return

        for attachment in attachments_without_messages:
            md5 = hashlib.md5()
            for chunk in attachment.document.file.chunks():
                md5.update(chunk)
            ATTACHMENT_HASH_MAP[md5.hexdigest()] = attachment.pk

        for message_record in orm['django_mailbox.message'].objects.all():
            message = email.message_from_string(message_record.body)
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    md5 = hashlib.md5()
                    md5.update(part.get_payload(decode=True))
                    digest = md5.hexdigest()
                    if digest in ATTACHMENT_HASH_MAP:
                        attachment = orm[
                            'django_mailbox.messageattachment'
                        ].objects.get(pk=ATTACHMENT_HASH_MAP[digest])
                        attachment.message = message_record
                        attachment.save()
                        logger.info(
                            "Associated message %s with attachment %s (%s)",
                            message_record.pk,
                            attachment.pk,
                            digest
                        )
                    else:
                        logger.info(
                            "%s(%s) not found in currently-stored attachments",
                            part.get_filename(),
                            digest
                        )

    def backwards(self, orm):
        # No backward migration necessary
        pass

    models = {
        u'django_mailbox.mailbox': {
            'Meta': {'object_name': 'Mailbox'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'from_email': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'django_mailbox.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'from_header': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'replies'", 'null': 'True', 'to': u"orm['django_mailbox.Message']"}),
            'mailbox': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['django_mailbox.Mailbox']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'outgoing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'read': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_header': ('django.db.models.fields.TextField', [], {})
        },
        u'django_mailbox.messageattachment': {
            'Meta': {'object_name': 'MessageAttachment'},
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attachments'", 'null': 'True', 'to': u"orm['django_mailbox.Message']"})
        }
    }

    complete_apps = ['django_mailbox']
