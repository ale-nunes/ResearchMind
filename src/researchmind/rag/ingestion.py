"""Load PDF, TXT, and Markdown files into page-aware text records."""

from pathlib import Path

from pypdf import PdfReader


def _ocr_pdf(source_path: Path) -> list[tuple[int, str]]:
    """OCR image-based PDF pages locally with Tesseract when selectable text is absent."""
    try:
        import fitz  # type: ignore[import-untyped]
        import pytesseract  # type: ignore[import-untyped]
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "This PDF is image-based and needs local OCR. Install the Python packages with "
            '`python -m pip install -e ".[dev,ocr]"` and install Tesseract OCR for Windows. '
            "Then make sure the tesseract executable is available on PATH."
        ) from exc

    language = __import__("os").environ.get("OCR_LANGUAGE", "por+eng")
    records: list[tuple[int, str]] = []
    document = fitz.open(source_path)
    try:
        for page_number, page in enumerate(document, start=1):
            # 2x rendering is a reasonable accuracy/CPU tradeoff for text-heavy pages.
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            text = pytesseract.image_to_string(image, lang=language)
            records.append((page_number, text))
    finally:
        document.close()
    return records


def read_source(path: str | Path) -> list[tuple[int, str]]:
    """Return (page number, text) records; OCR is used for image-only PDFs."""
    source_path = Path(path)
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")

    suffix = source_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(source_path))
        records = [
            (index, page.extract_text() or "") for index, page in enumerate(reader.pages, start=1)
        ]
        if not any(text.strip() for _, text in records):
            records = _ocr_pdf(source_path)
        if not any(text.strip() for _, text in records):
            raise ValueError(
                "No text could be extracted from this PDF, even after OCR. "
                "Check the PDF quality and OCR_LANGUAGE setting."
            )
        return records

    if suffix in {".txt", ".md", ".markdown"}:
        text = source_path.read_text(encoding="utf-8", errors="replace")
        return [(1, text)]

    raise ValueError(f"Unsupported file type: {suffix}. Use PDF, TXT, or Markdown.")
