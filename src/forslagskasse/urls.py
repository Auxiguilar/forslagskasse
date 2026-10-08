from django.urls import path
from . import views


app_name = "forslagskasse"

urlpatterns = [
    path("", views.index, name="index"),
]
