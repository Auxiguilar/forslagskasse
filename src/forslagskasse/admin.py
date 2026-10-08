from django.contrib import admin

from .models import Suggestion, Attachment


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "submitted_at")
    readonly_fields = ("title", "message", "submitted_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    # Stub
    ...
