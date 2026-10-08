from django.db import models


class Suggestion(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Forslag"
        verbose_name_plural = "Forslag"


class Attachment(models.Model):
    # Stub.
    ...