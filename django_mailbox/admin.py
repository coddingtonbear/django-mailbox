from django.conf import settings
from django.contrib import admin

from django_mailbox.models import Message, Mailbox

def get_new_mail(mailbox_admin, request, queryset):
    for mailbox in queryset.all():
        mailbox.get_new_mail()
get_new_mail.short_description = 'Get new mail'

class MailboxAdmin(admin.ModelAdmin):
    list_display = (
                'name',
                'uri',
            )
    actions = [get_new_mail]

class MessageAdmin(admin.ModelAdmin):
    list_display = (
                'subject',
                'from_address',
                'received',
                'mailbox',
            )
    ordering = ['-received']

if getattr(settings, 'DJANGO_MAILBOX_ADMIN_ENABLED', True):
    admin.site.register(Message, MessageAdmin)
    admin.site.register(Mailbox, MailboxAdmin)
