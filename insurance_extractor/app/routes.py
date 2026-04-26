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
from werkzeug.utils import secure_filename

from . import db
from .models import Document
from .services.docx_parser import extract_text_from_docx
from .services.text_normalizer import normalize_text
from .services.validator import validate_docx_upload


main_bp = Blueprint("main", __name__)


def build_unique_filename(original_filename):
    """Build a safe filename that will not overwrite previous uploads."""
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "document.docx"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short_uuid = uuid4().hex[:8]
    return f"{timestamp}_{short_uuid}_{safe_name}"


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("document")
        is_valid, error_message = validate_docx_upload(uploaded_file)

        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for("main.index"))

        stored_filename = build_unique_filename(uploaded_file.filename)
        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        saved_path = upload_folder / stored_filename

        uploaded_file.save(saved_path)

        try:
            raw_text = extract_text_from_docx(saved_path)
            text_content = normalize_text(raw_text)
        except Exception:
            # If python-docx cannot read the file, it is probably damaged or
            # only renamed to .docx. We do not keep such files in the MVP.
            saved_path.unlink(missing_ok=True)
            flash("Не удалось прочитать DOCX-файл. Проверьте файл и попробуйте снова.", "error")
            return redirect(url_for("main.index"))

        document = Document(
            original_filename=uploaded_file.filename,
            stored_filename=stored_filename,
            file_path=str(saved_path),
            text_content=text_content,
            status="uploaded",
        )
        db.session.add(document)
        db.session.commit()

        flash("Документ загружен.", "success")
        return redirect(url_for("main.document_detail", document_id=document.id))

    documents = Document.query.order_by(Document.created_at.desc()).all()
    return render_template("index.html", documents=documents)


@main_bp.route("/documents/<int:document_id>")
def document_detail(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        abort(404)

    return render_template("document.html", document=document)
