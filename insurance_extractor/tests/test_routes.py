from io import BytesIO

from docx import Document as DocxDocument

from app.models import Document


def make_docx_file() -> BytesIO:
    docx = DocxDocument()
    docx.add_paragraph("Договор страхования")
    docx.add_paragraph("Страхователь: Иванов Иван")

    file_stream = BytesIO()
    docx.save(file_stream)
    file_stream.seek(0)
    return file_stream


def test_index_page_opens(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Договоры страхования".encode("utf-8") in response.data


def test_docx_upload_creates_document(client, app):
    response = client.post(
        "/",
        data={"document": (make_docx_file(), "contract.docx")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Договор страхования".encode("utf-8") in response.data

    with app.app_context():
        document = Document.query.one()
        assert document.original_filename == "contract.docx"
        assert "Страхователь" in document.text_content
