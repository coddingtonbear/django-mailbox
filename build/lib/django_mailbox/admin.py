#!/usr/bin/env python

"""
Model configuration in application ``django_mailbox`` for administration
console.
"""

import logging

from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django_mailbox.models import MessageAttachment, Message, Mailbox
from django_mailbox.signals import message_received
from django_mailbox.utils import convert_header_to_unicode


logger = logging.getLogger(__name__)


def get_new_mail(mailbox_admin, request, queryset):
    queryset.get_new_mail()


get_new_mail.short_description = _('Get new mail')


def resend_message_received_signal(message_admin, request, queryset):
    for message in queryset.all():
        logger.debug('Resending \'message_received\' signal for %s' % message)
        message_received.send(sender=message_admin, message=message)


resend_message_received_signal.short_description = (
    _('Re-send message received signal')
)


class MailboxAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'uri',
        'from_email',
        'active',
        'last_polling',
    )
    readonly_fields = ['last_polling', ]
    actions = [get_new_mail]


class MessageAttachmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('message', )
    list_display = ('message', 'document',)


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0


class MessageAdmin(admin.ModelAdmin):
    def attachment_count(self, msg):
        return msg.attachments.count()

    attachment_count.short_description = _('Attachment count')

    def subject(self, msg):
        return convert_header_to_unicode(msg.subject)

    def envelope_headers(self, msg):
        email = msg.get_email_object()
        return '\n'.join(
            [('{}: {}'.format(h, v)) for h, v in email.items()]
        )

    inlines = [
        MessageAttachmentInline,
    ]
    list_display = (
        'subject',
        'processed',
        'read',
        'mailbox',
        'outgoing',
        'attachment_count',
    )
    ordering = ['-processed']
    list_filter = (
        'mailbox',
        'outgoing',
        'processed',
        'read',
    )
    exclude = (
        'body',
    )
    raw_id_fields = (
        'in_reply_to',
    )
    readonly_fields = (
        'envelope_headers',
        'text',
        'html',
    )
    actions = [resend_message_received_signal]


if getattr(settings, 'DJANGO_MAILBOX_ADMIN_ENABLED', True):
    admin.site.register(Message, MessageAdmin)
    admin.site.register(MessageAttachment, MessageAttachmentAdmin)
    admin.site.register(Mailbox, MailboxAdmin)
