import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from markupsafe import Markup, escape
from werkzeug.utils import secure_filename

from . import db
from .models import Document
from .services.docx_parser import extract_text_from_docx
from .services.pdf_parser import parse_pdf
from .services.regex_extractor import extract_all_fields
from .services.text_normalizer import normalize_text
from .services.validator import get_extension, validate_document_upload


main_bp = Blueprint("main", __name__)

FIELD_ORDER = [
    "contract_number",
    "contract_date",
    "period_start",
    "period_end",
    "insurer_inn",
    "policyholder_inn",
    "total_insured_amount",
    "total_insurance_premium",
]


def build_unique_filename(original_filename):
    """Build a safe filename that will not overwrite previous uploads."""
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "document"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short_uuid = uuid4().hex[:8]
    return f"{timestamp}_{short_uuid}_{safe_name}"


def extract_text_from_uploaded_document(file_path, extension):
    if extension == "docx":
        return extract_text_from_docx(file_path), None

    if extension == "pdf":
        parsed_pdf = parse_pdf(str(file_path))
        return parsed_pdf.full_text, parsed_pdf.warning

    raise ValueError("Unsupported file extension")


def load_extraction_data(document):
    if document.extraction_result_json:
        return json.loads(document.extraction_result_json)

    if not document.text_content:
        return {}

    result = extract_all_fields(document.text_content)
    document.extraction_result_json = result.to_json()
    db.session.commit()
    return result.to_dict()


def field_rows_from_extraction(extraction_data):
    rows = []
    for key in FIELD_ORDER:
        field = extraction_data.get(key)
        if field:
            rows.append(field)
    return rows


def source_texts_from_extraction(extraction_data):
    source_texts = []

    for key in FIELD_ORDER:
        field = extraction_data.get(key) or {}
        source_text = field.get("source_text")
        if source_text:
            source_texts.append(source_text)

    for field in extraction_data.get("pledge_agreements", []):
        source_text = field.get("source_text")
        if source_text:
            source_texts.append(source_text)

    return source_texts


def build_highlighted_text(text_content, source_texts):
    if not text_content:
        return Markup("")

    ranges: list[tuple[int, int]] = []
    for source_text in sorted(set(source_texts), key=len, reverse=True):
        source_text = source_text.strip()
        if not source_text:
            continue

        start = text_content.find(source_text)
        if start == -1:
            continue

        end = start + len(source_text)
        if any(start < existing_end and end > existing_start for existing_start, existing_end in ranges):
            continue

        ranges.append((start, end))

    ranges.sort()
    html_parts = []
    cursor = 0

    for start, end in ranges:
        html_parts.append(escape(text_content[cursor:start]))
        html_parts.append(f'<mark class="source-highlight">{escape(text_content[start:end])}</mark>')
        cursor = end

    html_parts.append(escape(text_content[cursor:]))
    return Markup("".join(str(part) for part in html_parts))


def build_copy_all_text(field_rows, pledge_fields):
    lines = ["Поле\tЗначение\tМетод\tConfidence\tПредупреждения"]

    for field in field_rows + pledge_fields:
        warnings = "; ".join(field.get("warnings") or [])
        lines.append(
            "\t".join(
                [
                    field.get("label") or field.get("name") or "",
                    field.get("value") or "",
                    field.get("method") or "",
                    str(field.get("confidence") if field.get("confidence") is not None else ""),
                    warnings,
                ]
            )
        )

    return "\n".join(lines)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("document")
        is_valid, error_message = validate_document_upload(uploaded_file)

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("main.index"))

        stored_filename = build_unique_filename(uploaded_file.filename)
        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        saved_path = upload_folder / stored_filename

        uploaded_file.save(saved_path)

        try:
            extension = get_extension(uploaded_file.filename)
            raw_text, parser_warning = extract_text_from_uploaded_document(saved_path, extension)
            text_content = normalize_text(raw_text)
            extraction_result = extract_all_fields(text_content)
        except Exception:
            # The file can be damaged or only renamed to a supported extension.
            # We remove it because there is no useful text to show in the MVP.
            saved_path.unlink(missing_ok=True)
            flash("Could not read this document. Check the file and try again.", "error")
            return redirect(url_for("main.index"))

        document = Document(
            original_filename=uploaded_file.filename,
            stored_filename=stored_filename,
            file_path=str(saved_path),
            text_content=text_content,
            extraction_result_json=extraction_result.to_json(),
            status="uploaded",
        )
        db.session.add(document)
        db.session.commit()

        if parser_warning:
            flash(parser_warning, "warning")
        else:
            flash("Document uploaded and fields extracted.", "success")

        return redirect(url_for("main.document_detail", document_id=document.id))

    documents = Document.query.order_by(Document.created_at.desc()).all()
    return render_template("index.html", documents=documents)


@main_bp.route("/documents/<int:document_id>")
def document_detail(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        abort(404)

    documents = Document.query.order_by(Document.created_at.desc()).all()
    extraction_data = load_extraction_data(document)
    field_rows = field_rows_from_extraction(extraction_data)
    pledge_fields = extraction_data.get("pledge_agreements", [])
    highlighted_text = build_highlighted_text(
        document.text_content or "",
        source_texts_from_extraction(extraction_data),
    )
    copy_all_text = build_copy_all_text(field_rows, pledge_fields)

    return render_template(
        "document.html",
        document=document,
        documents=documents,
        field_rows=field_rows,
        pledge_fields=pledge_fields,
        highlighted_text=highlighted_text,
        copy_all_text=copy_all_text,
    )
