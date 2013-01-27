import logging

from django.conf import settings
from django.contrib import admin

from django_mailbox.models import MessageAttachment, Message, Mailbox
from django_mailbox.signals import message_received

logger = logging.getLogger(__name__)

def get_new_mail(mailbox_admin, request, queryset):
    for mailbox in queryset.all():
        logger.debug('Receiving mail for %s' % mailbox)
        mailbox.get_new_mail()
get_new_mail.short_description = 'Get new mail'

def resend_message_received_signal(message_admin, request, queryset):
    for message in queryset.all():
        logger.debug('Resending \'message_received\' signal for %s' % message)
        message_received.send(sender=message_admin, message=message)
resend_message_received_signal.short_description = 'Re-send message received signal'

class MailboxAdmin(admin.ModelAdmin):
    list_display = (
                'name',
                'uri',
                'from_email',
                'active',
            )
    actions = [get_new_mail]

class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('document',)

class MessageAdmin(admin.ModelAdmin):
    list_display = (
                'subject',
                'processed',
                'read',
                'mailbox',
                'outgoing',
            )
    ordering = ['-processed']
    list_filter = (
            'mailbox',
            'outgoing',
            'processed',
            'read',
            )
    raw_id_fields = (
            'in_reply_to',
            'attachments', 
            )
    actions = [resend_message_received_signal]

if getattr(settings, 'DJANGO_MAILBOX_ADMIN_ENABLED', True):
    admin.site.register(Message, MessageAdmin)
    admin.site.register(MessageAttachment, MessageAttachmentAdmin)
    admin.site.register(Mailbox, MailboxAdmin)
