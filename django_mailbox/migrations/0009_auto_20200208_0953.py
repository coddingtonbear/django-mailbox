# Generated by Django 2.2.4 on 2020-02-08 09:53

from django.db import migrations, models
import django_mailbox.utils
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0008_auto_20190219_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='eml',
            field=models.FileField(help_text='Original full content of message', null=True, upload_to=functools.partial(django_mailbox.utils.get_save_path, *(), **{'setting': 'message_upload_to'}), verbose_name='Raw message contents'),
        ),
    ]