from django.contrib import admin
from .models import Campaign, CampaignRecipient


class CampaignRecipientInline(admin.TabularInline):
    model = CampaignRecipient
    extra = 0
    readonly_fields = ['contact', 'status', 'sent_at', 'error_message']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_recipients', 'sent_count', 'failed_count', 'created_at']
    list_filter = ['status']
    search_fields = ['name']
    readonly_fields = ['status', 'started_at', 'completed_at']
    inlines = [CampaignRecipientInline]


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'contact', 'status', 'sent_at']
    list_filter = ['status']
    search_fields = ['contact__name', 'contact__phone']
