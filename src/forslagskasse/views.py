from django.shortcuts import render, redirect
from django import forms

from .models import Suggestion, Attachment


# Magic V
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


# Make a form based on Suggestion model.
class SuggestionForm(forms.ModelForm):
    attachments = forms.FileField(
        label="Vedlegg",
        required=False,
        widget=MultipleFileInput,
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
        form = SuggestionForm(request.POST)

        if form.is_valid():
            suggestion = form.save()

            for uploaded_file in request.FILES.getlist("attachments"):
                Attachment.objects.create(
                    suggestion=suggestion,
                    file=uploaded_file,
                )

            return redirect("forslagskasse:index")
    else:
        form = SuggestionForm()

    # Give SuggestionForm as context to be used in index template.
    return render(request, "forslagskasse/index.html", {"form": form})
