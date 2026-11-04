from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from pathlib import Path

from .models import Suggestion, Attachment


# Hooks associated attachments to a given suggestion in the admin interface.
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ("download_link", "attachment_name")

    def get_fields(self, request, obj=None):
        if request.user.has_perm("forslagskasse.download_attachment"):
            return ("download_link",)
        return ("attachment_name",)

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

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

    @admin.display(description="Vedlegg")
    def attachment_name(self, obj):
        if obj and obj.file:
            return Path(obj.file.name).name
        return "Ingen fil"


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "submitted_at")
    readonly_fields = ("title", "message", "submitted_at")
    inlines = [AttachmentInline]
