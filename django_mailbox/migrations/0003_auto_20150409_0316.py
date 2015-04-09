# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0002_add_eml_to_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='eml',
            field=models.FileField(help_text='Original full content of message', upload_to=b'messages', null=True, verbose_name='Raw message contents'),
        ),
    ]
