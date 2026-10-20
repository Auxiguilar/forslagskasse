from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from pathlib import Path

from .models import Suggestion, Attachment


# Hooks associated attachments to a given suggestion in the admin interface.
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ("download_link",)
    readonly_fields = ("download_link",)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Vedlegg")
    def download_link(self, obj):
        if obj and obj.file:
            return format_html(
                '<a href="{}">Last ned</a>',
                reverse(
                    "forslagskasse:download_attachment",
                    args=[obj.pk],
                ),
            )
        return "Ingen fil"  


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "submitted_at")
    readonly_fields = ("title", "message", "submitted_at")
    inlines = [AttachmentInline]
