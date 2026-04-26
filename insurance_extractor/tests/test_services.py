from app.services.regex_extractor import extract_insurance_fields
from app.services.text_normalizer import normalize_text
from app.services.validator import has_allowed_extension


def test_has_allowed_extension_accepts_docx():
    assert has_allowed_extension("contract.docx")
    assert has_allowed_extension("CONTRACT.DOCX")


def test_has_allowed_extension_rejects_pdf():
    assert not has_allowed_extension("contract.pdf")


def test_normalize_text_compacts_spaces_and_empty_lines():
    raw_text = "  Договор   страхования\r\n\r\n\r\n  Номер\t123  "

    assert normalize_text(raw_text) == "Договор страхования\n\n Номер 123"


def test_regex_extractor_is_disabled_for_first_mvp():
    assert extract_insurance_fields("Любой текст") == {}
