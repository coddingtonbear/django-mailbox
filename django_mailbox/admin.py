from django.conf import settings
from django.contrib import admin

from django_mailbox.models import MessageAttachment, Message, Mailbox

def get_new_mail(mailbox_admin, request, queryset):
    for mailbox in queryset.all():
        mailbox.get_new_mail()
get_new_mail.short_description = 'Get new mail'

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
                'mailbox',
                'outgoing',
            )
    ordering = ['-processed']
    list_filter = (
            'mailbox',
            'outgoing',
            )
    raw_id_fields = (
            'in_reply_to',
            )

if getattr(settings, 'DJANGO_MAILBOX_ADMIN_ENABLED', True):
    admin.site.register(Message, MessageAdmin)
    admin.site.register(MessageAttachment, MessageAttachmentAdmin)
    admin.site.register(Mailbox, MailboxAdmin)
