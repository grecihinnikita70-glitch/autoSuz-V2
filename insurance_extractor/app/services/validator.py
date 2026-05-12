ALLOWED_EXTENSIONS = {"docx", "pdf"}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def has_allowed_extension(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_EXTENSIONS


def validate_document_upload(file_storage) -> tuple[bool, str | None]:
    if file_storage is None:
        return False, "File is not selected."

    filename = (file_storage.filename or "").strip()
    if not filename:
        return False, "File is not selected."

    if not has_allowed_extension(filename):
        return False, "Supported file formats: DOCX and text PDF."

    return True, None


def validate_docx_upload(file_storage) -> tuple[bool, str | None]:
    """Backward-compatible name used by older code and tests."""
    return validate_document_upload(file_storage)


def _add_warning_once(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def _date_to_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None

    parts = value.split(".")
    if len(parts) != 3:
        return None

    try:
        day, month, year = [int(part) for part in parts]
    except ValueError:
        return None

    if not 1 <= day <= 31 or not 1 <= month <= 12:
        return None

    return year, month, day


def _money_to_float(value: str | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def validate_extraction_result(result) -> None:
    """Add business warnings to an ExtractionResult in place."""
    inn_warning = "ИНН должен содержать 10 или 12 цифр."
    for inn_field in (result.insurer_inn, result.policyholder_inn):
        if inn_field.value and len(inn_field.value) not in {10, 12}:
            _add_warning_once(inn_field.warnings, inn_warning)

    date_warning = "Дата не распознана."
    for date_field in (result.contract_date, result.period_start, result.period_end):
        if date_field.value is None or _date_to_tuple(date_field.value) is None:
            _add_warning_once(date_field.warnings, date_warning)

    premium = _money_to_float(result.total_insurance_premium.value)
    insured_amount = _money_to_float(result.total_insured_amount.value)
    if premium is not None and insured_amount is not None and premium > insured_amount:
        _add_warning_once(
            result.total_insurance_premium.warnings,
            "Страховая премия больше страховой суммы.",
        )
        _add_warning_once(
            result.total_insured_amount.warnings,
            "Страховая сумма меньше страховой премии.",
        )

    if not result.pledge_agreements:
        _add_warning_once(
            result.contract_number.warnings,
            "Не найден ни один договор залога.",
        )

    period_start = _date_to_tuple(result.period_start.value)
    period_end = _date_to_tuple(result.period_end.value)
    if period_start is not None and period_end is not None and period_end < period_start:
        warning = "Дата окончания периода раньше даты начала."
        _add_warning_once(result.period_start.warnings, warning)
        _add_warning_once(result.period_end.warnings, warning)
