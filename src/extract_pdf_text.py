from pathlib import Path

from pypdf import PdfReader


def normalize_text(text: str) -> str:
    """Clean common PDF extraction artifacts while keeping the original meaning."""
    replacements = {
        "â€¢": "-",
        "\u2022": "-",
        "\uf0b7": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def extract_pdf_text(pdf_path: str | Path, max_pages: int = 8) -> str:
    """Extract readable text from the first pages of a PDF."""
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    page_count = min(len(reader.pages), max_pages)
    text_parts: list[str] = []

    for page_number in range(page_count):
        page = reader.pages[page_number]
        text = page.extract_text() or ""
        text_parts.append(text)

    return normalize_text("\n\n".join(text_parts)).strip()
