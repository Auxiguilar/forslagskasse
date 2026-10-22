from django import forms
from django.core.exceptions import ValidationError
from pathlib import Path

from .models import Suggestion
from .validation import *


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB
MAX_FILES = 5

ALLOWED_EXTENSIONS = {
    ".jpg", ".png", ".svg",
    ".doc", ".docx", ".pdf", ".odt",
    ".xls", ".xlsx", ".ods", ".txt",
}


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = {
            **(attrs or {}),
            "accept": ",".join(sorted(ALLOWED_EXTENSIONS)),
            "multiple": True,
        }
        super().__init__(attrs)


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
                    f"Filtypen '{extension}'' er ikke tillatt."
                )

            if extension in {".png", ".jpg"} and not validate_image(uploaded_file):
                raise ValidationError(
                    f"Filen '{uploaded_file.name}' er ikke et gyldig bilde."
                )

            if extension in {".docx", ".xlsx", ".odt", ".ods"}:
                if not validate_zip_document(uploaded_file, extension):
                    raise ValidationError(
                        f"Filen '{uploaded_file.name}' er ikke et gyldig dokument."
                    )

            if extension == ".svg" and not validate_svg(uploaded_file):
                raise ValidationError(
                    f"Filen '{uploaded_file.name}' er ikke en gyldig SVG-fil."
                )

            if extension in {".doc", ".xls"}:
                if not validate_ole_document(uploaded_file, extension):
                    raise ValidationError(
                        f"Filen '{uploaded_file.name}' er ikke et gyldig dokument."
                    )

            if extension == ".pdf" and not validate_pdf(uploaded_file):
                raise ValidationError(
                    f"Filen '{uploaded_file.name}' er ikke en gyldig PDF-fil."
                )

            if extension == ".txt" and not validate_text(uploaded_file):
                raise ValidationError(
                    f"Filen '{uploaded_file.name}' inneholder ugyldig tekst."
                )

            cleaned_files.append(uploaded_file)

        return cleaned_files


# Make a form based on Suggestion model.
class SuggestionForm(forms.ModelForm):
    attachments = MultipleFileField(
        label="Vedlegg",
        required=False,
        widget=MultipleFileInput(attrs={"id": "id_attachments"}),
    )

    class Meta:
        model = Suggestion
        fields = ["title", "message"]
        labels = {
            "title": "Tittel",
            "message": "Melding",
        }
        