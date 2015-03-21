# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='eml',
            field=models.FileField(help_text='Original full content of message', upload_to=b'messages', null=True, verbose_name='Message as a file'),
            preserve_default=True,
        ),
    ]
