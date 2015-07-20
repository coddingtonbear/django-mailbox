# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0003_auto_20150409_0316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='eml',
            field=models.FileField(verbose_name='Raw message contents', upload_to='messages', null=True, help_text='Original full content of message'),
        ),
        migrations.AlterField(
            model_name='messageattachment',
            name='document',
            field=models.FileField(verbose_name='Document', upload_to='mailbox_attachments/%Y/%m/%d/'),
        ),
    ]
