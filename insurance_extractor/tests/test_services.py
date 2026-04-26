from pathlib import Path

from docx import Document as DocxDocument

from app.services.docx_parser import parse_docx
from app.services.regex_extractor import extract_insurance_fields
from app.services.text_normalizer import normalize_text
from app.services.validator import has_allowed_extension


def test_has_allowed_extension_accepts_docx():
    assert has_allowed_extension("contract.docx")
    assert has_allowed_extension("CONTRACT.DOCX")


def test_has_allowed_extension_rejects_pdf():
    assert not has_allowed_extension("contract.pdf")


def test_normalize_text_compacts_spaces_and_empty_lines():
    raw_text = "  Insurance   contract\r\n\r\n\r\n  Number\t123  "

    assert normalize_text(raw_text) == "Insurance contract\n\n Number 123"


def test_regex_extractor_is_disabled_for_first_mvp():
    assert extract_insurance_fields("Any text") == {}


def test_parse_docx_keeps_paragraph_and_table_order():
    file_path = Path(__file__).resolve().parent / "ordered_test.docx"
    docx = DocxDocument()
    docx.add_paragraph("First paragraph")

    table = docx.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Name"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Policy"
    table.cell(1, 1).text = "123"

    docx.add_paragraph("Last paragraph")
    try:
        docx.save(file_path)

        parsed_document = parse_docx(file_path)

        assert parsed_document.paragraphs == ["First paragraph", "Last paragraph"]
        assert parsed_document.tables == [["Name\tValue", "Policy\t123"]]
        assert parsed_document.raw_blocks == [
            "First paragraph",
            "Name\tValue\nPolicy\t123",
            "Last paragraph",
        ]
        assert parsed_document.full_text == (
            "First paragraph\nName\tValue\nPolicy\t123\nLast paragraph"
        )
    finally:
        file_path.unlink(missing_ok=True)
