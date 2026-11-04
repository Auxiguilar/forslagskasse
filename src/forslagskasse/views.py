from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.http import FileResponse

from .models import Attachment
from .forms import SuggestionForm


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
    return render(
        request,
        "forslagskasse/index.html",
        {"form": form, "is_staff": request.user.is_staff}
    )


@staff_member_required
@permission_required({"forslagskasse.download_attachment"}, raise_exception=True)
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(Attachment, pk=attachment_id)

    return FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.file.name.split("/")[-1],
    )
