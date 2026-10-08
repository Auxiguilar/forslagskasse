from django.shortcuts import render, redirect
from django import forms

from .models import Suggestion


# Make a form based on Suggestion model.
class SuggestionForm(forms.ModelForm):
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
            form.save()
            return redirect("forslagskasse:index")
    else:
        form = SuggestionForm()

    # Give SuggestionForm as context to be used in index template.
    return render(request, "forslagskasse/index.html", {"form": form})
