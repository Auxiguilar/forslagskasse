from pathlib import Path
from zipfile import BadZipFile, ZipFile

from PIL import Image, UnidentifiedImageError
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from pypdf import PdfReader
from pypdf.errors import PyPdfError
from codecs import getincrementaldecoder
import olefile


ZIP_FORMATS = {
    ".docx": {
        "members": {"[Content_Types].xml", "word/document.xml"},
    },
    ".xlsx": {
        "members": {"[Content_Types].xml", "xl/workbook.xml"},
    },
    ".odt": {
        "members": {"mimetype", "content.xml", "META-INF/manifest.xml"},
        "mimetype": b"application/vnd.oasis.opendocument.text",
    },
    ".ods": {
        "members": {"mimetype", "content.xml", "META-INF/manifest.xml"},
        "mimetype": b"application/vnd.oasis.opendocument.spreadsheet",
    },
}


def validate_image(uploaded_file):
    try:
        with Image.open(uploaded_file) as image:
            extension = Path(uploaded_file.name).suffix.lower()
            expected_formats = {
                ".jpg": "JPEG",
                ".png": "PNG",
            }

            if image.format != expected_formats.get(extension):
                return False

            image.verify()
            return True

    except (UnidentifiedImageError, OSError, ValueError):
        return False

    finally:
        uploaded_file.seek(0)


def validate_zip_document(uploaded_file, extension):
    try:
        with ZipFile(uploaded_file) as archive:
            names = set(archive.namelist())
            requirements = ZIP_FORMATS[extension]

            if not requirements["members"].issubset(names):
                return False

            if archive.testzip() is not None:
                return False

            expected_mimetype = requirements.get("mimetype")
            if (
                expected_mimetype is not None
                and archive.read("mimetype") != expected_mimetype
            ):
                return False

        return True

    except (BadZipFile, OSError, KeyError, ValueError):
        return False

    finally:
        uploaded_file.seek(0)


def validate_svg(uploaded_file):
    try:
        root = ElementTree.fromstring(uploaded_file.read())
        return root.tag == "{http://www.w3.org/2000/svg}svg"

    except (
        ElementTree.ParseError,
        DefusedXmlException,
        ValueError,
        OSError,
    ):
        return False

    finally:
        uploaded_file.seek(0)


def validate_ole_document(uploaded_file, extension):
    expected_streams = {
        ".doc": {"worddocument"},
        ".xls": {"workbook", "book"},
    }

    try:
        if not olefile.isOleFile(uploaded_file):
            return False

        with olefile.OleFileIO(uploaded_file) as document:
            streams = {
                path[-1].lower()
                for path in document.listdir(
                    streams=True,
                    storages=False,
                )
            }

            return bool(streams & expected_streams[extension])

    except (OSError, ValueError):
        return False

    finally:
        uploaded_file.seek(0)


def validate_pdf(uploaded_file):
    try:
        document = PdfReader(uploaded_file, strict=True)
        return len(document.pages) > 0

    except (PyPdfError, ValueError, OSError):
        return False

    finally:
        uploaded_file.seek(0)


def validate_text(uploaded_file):
    decoder = getincrementaldecoder("utf-8-sig")()

    try:
        for chunk in uploaded_file.chunks():
            decoder.decode(chunk)

        decoder.decode(b"", final=True)
        return True

    except UnicodeDecodeError:
        return False

    finally:
        uploaded_file.seek(0)
