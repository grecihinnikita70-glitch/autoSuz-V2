from dataclasses import dataclass
from pathlib import Path

from docx import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph


@dataclass
class ParsedDocument:
    full_text: str
    paragraphs: list[str]
    tables: list[list[str]]
    raw_blocks: list[str]


def _iter_document_blocks(docx_document):
    """Yield top-level paragraphs and tables in the same order as in DOCX."""
    for child in docx_document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, docx_document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, docx_document)


def _table_to_rows(table: Table) -> list[str]:
    rows: list[str] = []

    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        row_text = "\t".join(cells).strip()
        if row_text:
            rows.append(row_text)

    return rows


def parse_docx(file_path: str | Path) -> ParsedDocument:
    """Parse a DOCX file into text, paragraphs, tables, and ordered blocks."""
    docx_document = DocxDocument(str(file_path))
    paragraphs: list[str] = []
    tables: list[list[str]] = []
    raw_blocks: list[str] = []

    for block in _iter_document_blocks(docx_document):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                paragraphs.append(text)
                raw_blocks.append(text)
        elif isinstance(block, Table):
            table_rows = _table_to_rows(block)
            if table_rows:
                tables.append(table_rows)
                raw_blocks.append("\n".join(table_rows))

    return ParsedDocument(
        full_text="\n".join(raw_blocks),
        paragraphs=paragraphs,
        tables=tables,
        raw_blocks=raw_blocks,
    )


def extract_text_from_docx(file_path: str | Path) -> str:
    """Read paragraphs and tables from a DOCX file as plain text."""
    return parse_docx(file_path).full_text
