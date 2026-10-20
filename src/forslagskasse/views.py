from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse
from django import forms
from pathlib import Path

from .models import Suggestion, Attachment


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB
MAX_FILES = 5

ALLOWED_EXTENSIONS = {
    ".jpg", ".png", ".svg",
    ".doc", ".docx", ".pdf", ".odt",
    ".xls", ".xlsx", ".ods", ".txt",
}


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []

        files = data if isinstance(data, (list, tuple)) else [data]

        if len(files) > MAX_FILES:
            raise ValidationError("Du kan laste opp maksimalt 5 filer.")

        cleaned_files = []

        for uploaded_file in files:
            uploaded_file = super().clean(uploaded_file, initial)

            if uploaded_file.size > MAX_FILE_SIZE:
                raise ValidationError(
                    f"Filen '{uploaded_file.name}' er større enn 5 MiB."
                )

            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"Filtypen «{extension}» er ikke tillatt."
                )

            cleaned_files.append(uploaded_file)

        return cleaned_files


# Make a form based on Suggestion model.
class SuggestionForm(forms.ModelForm):
    attachments = MultipleFileField(
        label="Vedlegg",
        required=False,
        widget=MultipleFileInput(),
    )

    class Meta:
        model = Suggestion
        fields = ["title", "message"]
        labels = {
            "title": "Tittel",
            "message": "Melding",
        }


def index(request):
    if request.method == "POST":
        form = SuggestionForm(request.POST, request.FILES)

        if form.is_valid():
            suggestion = form.save()

            for uploaded_file in form.cleaned_data["attachments"]:
                Attachment.objects.create(
                    suggestion=suggestion,
                    file=uploaded_file
                )

            return redirect("forslagskasse:index")
    else:
        form = SuggestionForm()

    # Give SuggestionForm as context to be used in index template.
    return render(request, "forslagskasse/index.html", {"form": form})


@staff_member_required
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(Attachment, pk=attachment_id)

    return FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.file.name.split("/")[-1],
    )

