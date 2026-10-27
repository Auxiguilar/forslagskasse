from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from pathlib import Path


class Suggestion(models.Model):
    title = models.CharField("Tittel", max_length=200)
    message = models.TextField("Forslag")
    submitted_at = models.DateTimeField("Innsendt", auto_now_add=True)

    class Meta:
        verbose_name = "Forslag"
        verbose_name_plural = "Forslag"

    def __str__(self) -> str:
        return self.title


class Attachment(models.Model):
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField("Fil", upload_to="vedlegg/")

    class Meta:
        verbose_name = "Vedlegg"
        verbose_name_plural = "Vedlegg"

    def __str__(self) -> str:
        return Path(self.file.name).name


# Immediate deletion!
@receiver(post_delete, sender=Attachment)
def delete_attachment_file(sender, instance, **kwargs):
    if instance.file:
        file_name = instance.file.name
        storage = instance.file.storage
        storage.delete(file_name)