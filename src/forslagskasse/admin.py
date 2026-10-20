from django.contrib import admin

from .models import Suggestion, Attachment


# Hooks associated attachments to a given suggestion in the admin interface.
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ("file",)
    can_delete = False


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "submitted_at")
    readonly_fields = ("title", "message", "submitted_at")
    inlines = [AttachmentInline]
