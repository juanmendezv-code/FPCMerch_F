from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("subject", "is_read", "created_at")
    search_fields = ("name", "email", "message")
    list_editable = ("is_read",)
