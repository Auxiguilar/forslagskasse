
import tempfile

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from .models import Suggestion, Attachment
from .views import SuggestionForm


class SuggestionModelTests(TestCase):
    """Tests for the Suggestion model."""

    def test_string_representation(self):
        suggestion = Suggestion(
            title="Testforslag",
            message="Dette er en test.",
        )

        self.assertEqual(str(suggestion), "Testforslag")

    def test_suggestion_can_be_saved(self):
        suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )

        self.assertIsNotNone(suggestion.pk)
        self.assertEqual(suggestion.title, "Testforslag")


class AttachmentModelTests(TestCase):
    """Tests for the Attachment model."""

    def test_string_representation_is_filename(self):
        attachment = Attachment(
            file="forslag_vedlegg/rapport.pdf",
        )

        self.assertEqual(str(attachment), "rapport.pdf")

    def test_attachment_belongs_to_suggestion(self):
        suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )

        attachment = Attachment.objects.create(
            suggestion=suggestion,
            file="forslag_vedlegg/rapport.pdf",
        )

        self.assertEqual(attachment.suggestion, suggestion)
        self.assertIn(attachment, suggestion.attachments.all()) # type: ignore


class SuggestionFormTests(TestCase):
    """Tests for the suggestion submission form."""

    def test_valid_form(self):
        form = SuggestionForm(data={
            "title": "Testforslag",
            "message": "Dette er en test.",
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_title_is_required(self):
        form = SuggestionForm(data={
            "title": "",
            "message": "Dette er en test.",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_message_is_required(self):
        form = SuggestionForm(data={
            "title": "Testforslag",
            "message": "",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_valid_attachment_is_accepted(self):
        uploaded_file = SimpleUploadedFile(
            "rapport.pdf",
            b"Testinnhold",
            content_type="application/pdf",
        )

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette er en test.",
            },
            files=MultiValueDict({
                "attachments": [uploaded_file],
            }),
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_disallowed_extension_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            "program.exe",
            b"Testinnhold",
            content_type="application/octet-stream",
        )

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette er en test.",
            },
            files=MultiValueDict({
                "attachments": [uploaded_file],
            }),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)

    
    def make_upload(self, name="report.txt", size=10):
        return SimpleUploadedFile(
            name,
            b"x" * size,
            content_type="text/plain",
        )


    def test_six_attachments_are_rejected(self):
        files = [
            self.make_upload(f"report{i}.txt")
            for i in range(6)
        ]

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette er en test.",
            },
            files=MultiValueDict({"attachments": files}), # type: ignore
        )

        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)


    def test_five_attachments_are_accepted(self):
        files = [
            self.make_upload(f"report{i}.txt")
            for i in range(5)
        ]

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette er en test.",
            },
            files=MultiValueDict({"attachments": files}), # type: ignore
        )

        self.assertTrue(form.is_valid(), form.errors)


    def test_oversized_attachment_is_rejected(self):
        from .views import MAX_FILE_SIZE

        uploaded_file = self.make_upload(
            "large.txt",
            MAX_FILE_SIZE + 1,
        )

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette is a test.",
            },
            files=MultiValueDict({"attachments": [uploaded_file]}),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)


    def test_attachment_at_size_limit_is_accepted(self):
        from .views import MAX_FILE_SIZE

        uploaded_file = self.make_upload(
            "limit.txt",
            MAX_FILE_SIZE,
        )

        form = SuggestionForm(
            data={
                "title": "Testforslag",
                "message": "Dette er en test.",
            },
            files=MultiValueDict({"attachments": [uploaded_file]}),
        )

        self.assertTrue(form.is_valid(), form.errors)


class AttachmentDownloadTests(TestCase):
    """Tests for the staff-protected download view."""

    def setUp(self):
        # Keep test uploads out of real media directory.
        self.temp_media = tempfile.TemporaryDirectory()
        self.media_settings = override_settings(
            MEDIA_ROOT=self.temp_media.name,
        )
        self.media_settings.enable()

        self.addCleanup(self.media_settings.disable)
        self.addCleanup(self.temp_media.cleanup)

        self.suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )

        self.attachment = Attachment.objects.create(
            suggestion=self.suggestion,
            file=SimpleUploadedFile(
                "rapport.pdf",
                b"Test file contents",
                content_type="application/pdf",
            ),
        )

        self.url = reverse(
            "forslagskasse:download_attachment",
            args=[self.attachment.pk],
        )

    def test_anonymous_user_cannot_download(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_download(self):
        User = get_user_model()
        User.objects.create_user(
            username="testadmin",
            password="test-password",
            is_staff=True,
        )

        self.client.login(
            username="testadmin",
            password="test-password",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )
        self.assertIn(
            "rapport.pdf",
            response["Content-Disposition"],
        )

        downloaded_content = b"".join(response.streaming_content) # type: ignore
        self.assertEqual(downloaded_content, b"Test file contents")