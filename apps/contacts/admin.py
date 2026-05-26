from django.contrib import admin
from .models import Contact, ContactGroup


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'groups']
    search_fields = ['name', 'phone']
    filter_horizontal = ['groups']
