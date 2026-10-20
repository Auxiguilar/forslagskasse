from django.db import models


class Suggestion(models.Model):
    title = models.CharField("Tittel", max_length=200)
    message = models.TextField("Forslag")
    submitted_at = models.DateTimeField("Innsendt", auto_now_add=True)

    class Meta:
        verbose_name = "Forslag"
        verbose_name_plural = "Forslag"


class Attachment(models.Model):
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField("Fil", upload_to="suggestions/")

    class Meta:
        verbose_name = "Vedlegg"
        verbose_name_plural = "Vedlegg"
    