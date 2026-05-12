from dataclasses import dataclass

import pdfplumber


SCAN_WARNING = "Text was not extracted. The PDF may be a scanned document; OCR is not enabled yet."


@dataclass
class PdfWord:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float
    page_number: int


@dataclass
class ParsedPdfPage:
    page_number: int
    text: str
    words: list[PdfWord]


@dataclass
class ParsedPdfDocument:
    full_text: str
    pages: list[ParsedPdfPage]
    warning: str | None = None


def _parse_word(word_data: dict, page_number: int) -> PdfWord:
    """Convert one pdfplumber word dictionary into a small dataclass."""
    return PdfWord(
        text=str(word_data.get("text", "")),
        x0=float(word_data.get("x0", 0)),
        top=float(word_data.get("top", 0)),
        x1=float(word_data.get("x1", 0)),
        bottom=float(word_data.get("bottom", 0)),
        page_number=page_number,
    )


def parse_pdf(file_path: str) -> ParsedPdfDocument:
    """Parse a text-based PDF and keep page/word coordinates.

    OCR is intentionally not used here. If the document is a scan, pdfplumber
    usually returns empty text; in that case we return a warning for the UI or
    debug script.
    """
    pages: list[ParsedPdfPage] = []
    page_texts: list[str] = []

    with pdfplumber.open(str(file_path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            raw_words = page.extract_words() or []
            words = [_parse_word(word_data, page_number) for word_data in raw_words]

            pages.append(
                ParsedPdfPage(
                    page_number=page_number,
                    text=text,
                    words=words,
                )
            )

            if text.strip():
                page_texts.append(text.strip())

    full_text = "\n\n".join(page_texts)
    warning = None
    if not full_text.strip():
        warning = SCAN_WARNING

    return ParsedPdfDocument(full_text=full_text, pages=pages, warning=warning)
