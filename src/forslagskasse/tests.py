import tempfile
import os
import importlib

from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from .models import Suggestion, Attachment
from .views import SuggestionForm
from .forms import MAX_FILE_SIZE


TEST_MEDIA_DIR = Path(__file__).parent / "test_media"


class CookieSettingsTests(TestCase):
    """Production cookie settings should be secure when debug is off."""

    def test_secure_cookies_are_enabled_in_production(self):
        import config.settings as settings_module

        original = {
            "DEBUG": os.environ.get("DEBUG"),
            "DJANGO_SECRET_KEY": os.environ.get("DJANGO_SECRET_KEY"),
        }

        try:
            os.environ["DEBUG"] = "False"
            os.environ["DJANGO_SECRET_KEY"] = "test-secret-key"
            importlib.reload(settings_module)
            self.assertTrue(settings_module.SESSION_COOKIE_SECURE)
            self.assertTrue(settings_module.CSRF_COOKIE_SECURE)
            self.assertEqual(settings_module.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))
        finally:
            for key, value in original.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            importlib.reload(settings_module)


def make_sample_upload(extension):
    path = TEST_MEDIA_DIR / f"sample.{extension}"
    return SimpleUploadedFile(
        path.name,
        path.read_bytes(),
        content_type="application/octet-stream",
    )


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
            file="vedlegg/rapport.pdf",
        )

        self.assertEqual(str(attachment), "rapport.pdf")

    def test_attachment_belongs_to_suggestion(self):
        suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )

        attachment = Attachment.objects.create(
            suggestion=suggestion,
            file="vedlegg/rapport.pdf",
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

    # Most embarrassing if my program generates false positives for invalidity!
    def test_valid_attachments_are_accepted(self):
        extensions = (
        "jpg", "png", "svg",
        "doc", "docx", "xls", "xlsx",
        "pdf", "odt", "ods", "txt",
        )

        for extension in extensions:
            with self.subTest(extension=extension):
                uploaded_file = make_sample_upload(extension)

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
                "rapport.txt",
                b"Test file contents",
                content_type="text/plain",
            ),
        )

        self.url = reverse(
            "forslagskasse:download_attachment",
            args=[self.attachment.pk],
        )

    def create_staff_user(self, username, permission_codenames):
        User = get_user_model()
        user = User.objects.create_user(
            username=username,
            password="test-password",
            is_staff=True,
        )
        permissions = Permission.objects.filter(
            content_type__app_label="forslagskasse",
            codename__in=permission_codenames,
        )
        user.user_permissions.add(*permissions)
        self.client.force_login(user)
        return user

    def test_view_only_staff_sees_filename_without_download_link(self):
        self.create_staff_user(
            "testviewer",
            ["view_suggestion", "view_attachment"],
        )

        response = self.client.get(
            reverse(
                "admin:forslagskasse_suggestion_change",
                args=[self.suggestion.pk],
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rapport.txt")
        self.assertNotContains(response, "Last ned")
        self.assertNotContains(response, self.url)

    def test_download_permission_shows_download_link_in_admin(self):
        self.create_staff_user(
            "testdownloader",
            ["view_suggestion", "view_attachment", "download_attachment"],
        )

        response = self.client.get(
            reverse(
                "admin:forslagskasse_suggestion_change",
                args=[self.suggestion.pk],
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Last ned")
        self.assertContains(response, self.url)

    def test_anonymous_user_cannot_download(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_download(self):
        self.create_staff_user(
            "testadmin",
            ["download_attachment"],
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )
        self.assertIn(
            "rapport.txt",
            response["Content-Disposition"],
        )

        downloaded_content = b"".join(response.streaming_content) # type: ignore
        self.assertEqual(downloaded_content, b"Test file contents")

class AttachmentDeletionTests(TestCase):
    def test_deleting_attachment_deletes_file(self):
        suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )

        attachment = Attachment.objects.create(
            suggestion=suggestion,
            file=SimpleUploadedFile(
                "rapport.txt",
                b"Test file contents",
            ),
        )
        file_path = attachment.file.path

        attachment.delete()

        self.assertFalse(os.path.exists(file_path))


    def test_deleting_suggestion_deletes_attachment_files(self):
        suggestion = Suggestion.objects.create(
            title="Testforslag",
            message="Dette er en test.",
        )
                
        attachment = Attachment.objects.create(
            suggestion=suggestion,
            file=SimpleUploadedFile(
                "rapport.txt",
                b"Test file contents",
            ),
        )
        file_path = attachment.file.path

        suggestion.delete()

        self.assertFalse(os.path.exists(file_path))
        self.assertFalse(Attachment.objects.filter(pk=attachment.pk).exists())
