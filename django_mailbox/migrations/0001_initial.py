# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mailbox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('uri', models.CharField(default=None, max_length=255, blank=True, help_text="Example: imap+ssl://myusername:mypassword@someserver <br /><br />Internet transports include 'imap' and 'pop3'; common local file transports include 'maildir', 'mbox', and less commonly 'babyl', 'mh', and 'mmdf'. <br /><br />Be sure to urlencode your username and password should they contain illegal characters (like @, :, etc).", null=True, verbose_name='URI')),
                ('from_email', models.CharField(default=None, max_length=255, blank=True, help_text="Example: MailBot &lt;mailbot@yourdomain.com&gt;<br />'From' header to set for outgoing email.<br /><br />If you do not use this e-mail inbox for outgoing mail, this setting is unnecessary.<br />If you send e-mail without setting this, your 'From' header will'be set to match the setting `DEFAULT_FROM_EMAIL`.", null=True, verbose_name='From email')),
                ('active', models.BooleanField(default=True, help_text='Check this e-mail inbox for new e-mail messages during polling cycles.  This checkbox does not have an effect upon whether mail is collected here when this mailbox receives mail from a pipe, and does not affect whether e-mail messages can be dispatched from this mailbox. ', verbose_name='Active')),
            ],
            options={
                'verbose_name_plural': 'Mailboxes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
                ('message_id', models.CharField(max_length=255, verbose_name='Message ID')),
                ('from_header', models.CharField(max_length=255, verbose_name='From header')),
                ('to_header', models.TextField(verbose_name='To header')),
                ('outgoing', models.BooleanField(default=False, verbose_name='Outgoing')),
                ('body', models.TextField(verbose_name='Body')),
                ('encoded', models.BooleanField(default=False, help_text='True if the e-mail body is Base64 encoded', verbose_name='Encoded')),
                ('processed', models.DateTimeField(auto_now_add=True, verbose_name='Processed')),
                ('read', models.DateTimeField(default=None, null=True, verbose_name='Read', blank=True)),
                ('in_reply_to', models.ForeignKey(related_name='replies', verbose_name='In reply to', blank=True, to='django_mailbox.Message', null=True)),
                ('mailbox', models.ForeignKey(related_name='messages', verbose_name='Mailbox', to='django_mailbox.Mailbox')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('headers', models.TextField(null=True, verbose_name='Headers', blank=True)),
                ('document', models.FileField(upload_to=b'mailbox_attachments/%Y/%m/%d/', verbose_name='Document')),
                ('message', models.ForeignKey(related_name='attachments', verbose_name='Message', blank=True, to='django_mailbox.Message', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
