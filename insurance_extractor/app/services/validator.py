ALLOWED_EXTENSIONS = {"docx"}


def has_allowed_extension(filename: str) -> bool:
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def validate_docx_upload(file_storage) -> tuple[bool, str | None]:
    if file_storage is None:
        return False, "Файл не выбран."

    filename = (file_storage.filename or "").strip()
    if not filename:
        return False, "Файл не выбран."

    if not has_allowed_extension(filename):
        return False, "На первом этапе поддерживаются только DOCX-файлы."

    return True, None
