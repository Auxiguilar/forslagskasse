from django.urls import path
from . import views


app_name = "forslagskasse"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "attachments/<int:attachment_id>/download/",
        views.download_attachment,
        name="download_attachment"
    )
]
