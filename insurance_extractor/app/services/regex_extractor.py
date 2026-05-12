import re
from decimal import Decimal, InvalidOperation

from .extraction_types import ExtractedField, ExtractionResult
from .validator import validate_extraction_result


SEARCH_LIMIT = 3000
DATE_SEARCH_LIMIT = 4000
CONTRACT_NUMBER_NAME = "contract_number"
CONTRACT_NUMBER_LABEL = "Номер договора/полиса"
CONTRACT_DATE_NAME = "contract_date"
CONTRACT_DATE_LABEL = "Дата договора/полиса"
PERIOD_START_NAME = "period_start"
PERIOD_START_LABEL = "Начало периода страхования"
PERIOD_END_NAME = "period_end"
PERIOD_END_LABEL = "Окончание периода страхования"
TOTAL_INSURED_AMOUNT_NAME = "total_insured_amount"
TOTAL_INSURED_AMOUNT_LABEL = "Общая страховая сумма"
TOTAL_INSURANCE_PREMIUM_NAME = "total_insurance_premium"
TOTAL_INSURANCE_PREMIUM_LABEL = "Общая страховая премия"
PLEDGE_AGREEMENT_NAME = "pledge_agreement"
PLEDGE_AGREEMENT_LABEL = "Договор залога/ипотеки"
INSURER_INN_NAME = "insurer_inn"
INSURER_INN_LABEL = "ИНН страховщика"
POLICYHOLDER_INN_NAME = "policyholder_inn"
POLICYHOLDER_INN_LABEL = "ИНН страхователя"

NO_SIGN_RE = re.compile(r"№\s*")
INSURANCE_LABEL_RE = re.compile(r"\b(договор\w*|полис\w*)\b", re.IGNORECASE)
EXCLUDED_CONTEXT_RE = re.compile(
    r"("
    r"кредит\w*\s+(?:\S+\s+){0,3}договор\w*"
    r"|договор\w*\s+(?:\S+\s+){0,3}кредит\w*"
    r"|залог\w*\s+(?:\S+\s+){0,3}договор\w*"
    r"|договор\w*\s+(?:\S+\s+){0,3}залог\w*"
    r"|ипотек\w*"
    r")",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9][A-Za-zА-Яа-яЁё0-9/\- ]{3,100}")
STOP_AFTER_NUMBER_RE = re.compile(
    r"\s+(от|дата|заключ[её]н|выдан|срок|период|страховани[яе]|по|к|г\.?|следующ\w*)\b",
    re.IGNORECASE,
)
MONTHS = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}
MONTH_PATTERN = "|".join(MONTHS)
DATE_TEXT_RE = re.compile(
    rf"[«\"]?\s*(?P<day>\d{{1,2}})\s*[»\"]?\s+"
    rf"(?P<month>{MONTH_PATTERN})\s+"
    r"(?P<year>\d{4})\s*(?:г\.?|года)?",
    re.IGNORECASE,
)
EXCLUDED_DATE_CONTEXT_RE = re.compile(
    r"доверенн\w*|правил\w*\s+страхован\w*|страхов\w*\s+правил\w*",
    re.IGNORECASE,
)
NUMERIC_DATE_RE = re.compile(
    r"(?<![\d./-])(?P<day>\d{1,2})\s*[.]\s*"
    r"(?P<month>\d{1,2})\s*[.]\s*"
    r"(?P<year>\d{4})(?![\d./-])"
)
PERIOD_MARKER_RE = re.compile(
    r"период\s+страхования|срок\s+действия\s+(?:полиса|договора)",
    re.IGNORECASE,
)
EXCLUDED_PERIOD_CONTEXT_RE = re.compile(
    r"кредит\w*|залог\w*|ипотек\w*|доверенн\w*",
    re.IGNORECASE,
)
MONEY_RE = re.compile(
    r"(?<![\w/.-])(?P<amount>\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:,\d{2})?|\d+,\d{2})(?![\w/.-])"
)
EXPLICIT_INSURED_AMOUNT_RE = re.compile(
    r"(?:итого\s+)?общая\s+страховая\s+сумма\b[^\n]{0,180}",
    re.IGNORECASE,
)
SOFT_INSURED_AMOUNT_RE = re.compile(
    r"\bстраховая\s+сумма\b[^\n]{0,180}",
    re.IGNORECASE,
)
EXPLICIT_PREMIUM_RE = re.compile(
    r"(?:(?:итого\s+)?общая\s+страховая\s+премия|совокупная\s+страховая\s+премия)\b[^\n]{0,220}",
    re.IGNORECASE,
)
SOFT_PREMIUM_RE = re.compile(
    r"\bстраховая\s+премия\b[^\n]{0,180}",
    re.IGNORECASE,
)
EXCLUDED_AMOUNT_CONTEXT_RE = re.compile(
    r"франшиз\w*|страхов\w*\s+взнос\w*|очередн\w*\s+взнос\w*|перв\w*\s+взнос\w*",
    re.IGNORECASE,
)
PLEDGE_CONTEXT_RE = re.compile(
    r"договор\w*\s+залога|договор\w*\s+об\s+ипотек\w*|последующ\w*\s+ипотек\w*|предмет\w*\s+залога",
    re.IGNORECASE,
)
CREDIT_CONTEXT_RE = re.compile(
    r"кредитн\w*\s+(?:соглашен\w*|договор\w*)|(?:соглашен\w*|договор\w*)\s+кредитн\w*",
    re.IGNORECASE,
)
PLEDGE_NUMBER_RE = re.compile(
    r"(?<![\w/-])"
    r"("
    r"[A-Za-zА-Яа-яЁё]{2,6}/\d{2,6}-\d{2,6}(?:-\d{2,6})?"
    r"|[A-Za-zА-Яа-яЁё]{1,4}\d{0,4}-[A-Za-zА-Яа-яЁё]{1,4}-\d{3,8}/\d{4}/\d{3,8}"
    r"|\d{1,4}/\d{1,4}/\d{1,4}/\d{1,4}"
    r"|[A-Za-zА-Яа-яЁё]{1,6}/\d{2,4}-\d{2,4}/\d{2,4}-\d{2,6}-\d{2,6}"
    r")"
    r"(?![\w/-])",
    re.IGNORECASE,
)
INN_RE = re.compile(r"(?<!\d)(\d{10}|\d{12}|\d{8,14})(?!\d)")
INSURER_CONTEXT_RE = re.compile(r"страховщик\w*", re.IGNORECASE)
POLICYHOLDER_CONTEXT_RE = re.compile(r"страхователь\w*", re.IGNORECASE)


def _not_found_contract_number() -> ExtractedField:
    return ExtractedField(
        name=CONTRACT_NUMBER_NAME,
        label=CONTRACT_NUMBER_LABEL,
    )


def _not_found_contract_date() -> ExtractedField:
    return ExtractedField(
        name=CONTRACT_DATE_NAME,
        label=CONTRACT_DATE_LABEL,
    )


def _not_found_period_start() -> ExtractedField:
    return ExtractedField(
        name=PERIOD_START_NAME,
        label=PERIOD_START_LABEL,
    )


def _not_found_period_end() -> ExtractedField:
    return ExtractedField(
        name=PERIOD_END_NAME,
        label=PERIOD_END_LABEL,
    )


def _not_found_total_insured_amount() -> ExtractedField:
    return ExtractedField(
        name=TOTAL_INSURED_AMOUNT_NAME,
        label=TOTAL_INSURED_AMOUNT_LABEL,
    )


def _not_found_total_insurance_premium() -> ExtractedField:
    return ExtractedField(
        name=TOTAL_INSURANCE_PREMIUM_NAME,
        label=TOTAL_INSURANCE_PREMIUM_LABEL,
    )


def _not_found_insurer_inn() -> ExtractedField:
    return ExtractedField(
        name=INSURER_INN_NAME,
        label=INSURER_INN_LABEL,
    )


def _not_found_policyholder_inn() -> ExtractedField:
    return ExtractedField(
        name=POLICYHOLDER_INN_NAME,
        label=POLICYHOLDER_INN_LABEL,
    )


def _iter_fragments(text: str):
    """Yield short readable fragments that contain the number sign."""
    limited_text = text[:SEARCH_LIMIT].replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in limited_text.split("\n")]

    for index, line in enumerate(lines):
        if "№" not in line:
            continue

        parts: list[str] = []
        if index > 0 and lines[index - 1] and "№" not in lines[index - 1]:
            parts.append(lines[index - 1])

        parts.append(line)

        # Sometimes the heading is on one line and the number continues on the
        # next. Adding one following line keeps this case easy to support.
        if (
            index + 1 < len(lines)
            and lines[index + 1]
            and "№" not in lines[index + 1]
            and len(line) < 120
        ):
            parts.append(lines[index + 1])

        yield " ".join(parts)


def _make_source_text(fragment: str, number_sign_position: int) -> str:
    start = max(0, number_sign_position - 140)
    end = min(len(fragment), number_sign_position + 160)
    return re.sub(r"\s+", " ", fragment[start:end]).strip()


def _is_excluded_date_context(text: str, date_position: int) -> bool:
    line_start = text.rfind("\n", 0, date_position) + 1
    line_end = text.find("\n", date_position)
    if line_end == -1:
        line_end = len(text)

    context_parts = [text[line_start:line_end]]
    previous_line_end = line_start - 1

    if previous_line_end > 0:
        previous_line_start = text.rfind("\n", 0, previous_line_end) + 1
        previous_line = text[previous_line_start:previous_line_end].strip()
        if previous_line and not DATE_TEXT_RE.search(previous_line):
            context_parts.insert(0, previous_line)

    context = " ".join(context_parts)
    return bool(EXCLUDED_DATE_CONTEXT_RE.search(context))


def _is_excluded_context(fragment: str, number_sign_position: int) -> bool:
    before_number = fragment[max(0, number_sign_position - 120) : number_sign_position]
    return bool(EXCLUDED_CONTEXT_RE.search(before_number))


def _is_excluded_period_context(source_text: str) -> bool:
    return bool(EXCLUDED_PERIOD_CONTEXT_RE.search(source_text))


def _has_insurance_label(fragment: str, number_sign_position: int) -> bool:
    around_number = fragment[max(0, number_sign_position - 180) : number_sign_position + 180]
    return bool(INSURANCE_LABEL_RE.search(around_number))


def _clean_contract_number(raw_number: str) -> str:
    raw_number = STOP_AFTER_NUMBER_RE.split(raw_number, maxsplit=1)[0]
    raw_number = re.split(r"[;,:]", raw_number, maxsplit=1)[0]
    raw_number = raw_number.strip(" .\t\n")
    raw_number = re.sub(r"\s+", " ", raw_number)
    raw_number = re.sub(r"\s*([/-])\s*", r"\1", raw_number)
    first_token = raw_number.split(" ", maxsplit=1)[0]
    if "/" in first_token or "-" in first_token:
        return first_token.strip()

    return raw_number.strip()


def _extract_number_after_sign(fragment: str, number_sign_position: int) -> str | None:
    after_number_sign = fragment[number_sign_position:]
    match = NUMBER_RE.match(after_number_sign)
    if not match:
        return None

    contract_number = _clean_contract_number(match.group(0))
    compact_number = contract_number.replace(" ", "")

    if len(compact_number) < 5:
        return None

    if not any(char.isdigit() for char in compact_number):
        return None

    return contract_number


def _build_date_value(day: int, month: int, year: str) -> str | None:
    if not 1 <= day <= 31 or not 1 <= month <= 12:
        return None

    return f"{day:02d}.{month:02d}.{year}"


def _iter_date_matches(text: str):
    """Yield dates with positions from a text fragment in reading order."""
    found_dates: list[tuple[int, int, str]] = []

    for match in DATE_TEXT_RE.finditer(text):
        day = int(match.group("day"))
        month = int(MONTHS[match.group("month").lower()])
        value = _build_date_value(day, month, match.group("year"))
        if value:
            found_dates.append((match.start(), match.end(), value))

    for match in NUMERIC_DATE_RE.finditer(text):
        day = int(match.group("day"))
        month = int(match.group("month"))
        value = _build_date_value(day, month, match.group("year"))
        if value:
            found_dates.append((match.start(), match.end(), value))

    yield from sorted(found_dates, key=lambda item: item[0])


def _extract_period_from_segment(segment: str) -> tuple[str, str, str] | None:
    for start_match in re.finditer(r"\bс\b", segment, re.IGNORECASE):
        window = segment[start_match.start() : start_match.start() + 900]
        dates = list(_iter_date_matches(window))
        if len(dates) < 2:
            continue

        start_date: tuple[int, int, str] | None = None
        end_date: tuple[int, int, str] | None = None

        for date_index in range(len(dates) - 1):
            possible_start = dates[date_index]
            possible_end = dates[date_index + 1]
            text_between_dates = window[possible_start[1] : possible_end[0]]

            for po_match in re.finditer(r"\bпо\b", text_between_dates, re.IGNORECASE):
                # In a real period phrase the end date follows "по" closely:
                # either immediately or after a short time phrase like
                # "24:00 часов".
                if possible_end[0] - (possible_start[1] + po_match.end()) <= 90:
                    start_date = possible_start
                    end_date = possible_end
                    break

            if start_date and end_date:
                break

        if not start_date or not end_date:
            continue

        source_end = start_match.start() + end_date[1]
        line_start = segment.rfind("\n", 0, start_match.start()) + 1
        context_source_text = re.sub(r"\s+", " ", segment[line_start:source_end]).strip()
        source_text = re.sub(r"\s+", " ", window[: end_date[1]]).strip()

        if _is_excluded_period_context(context_source_text):
            continue

        return start_date[2], end_date[2], source_text

    return None


def _make_period_fields(
    start_value: str,
    end_value: str,
    confidence: float,
    source_text: str,
) -> tuple[ExtractedField, ExtractedField]:
    period_start = ExtractedField(
        name=PERIOD_START_NAME,
        label=PERIOD_START_LABEL,
        value=start_value,
        confidence=confidence,
        method="regex",
        source_text=source_text,
        warnings=[],
    )
    period_end = ExtractedField(
        name=PERIOD_END_NAME,
        label=PERIOD_END_LABEL,
        value=end_value,
        confidence=confidence,
        method="regex",
        source_text=source_text,
        warnings=[],
    )
    return period_start, period_end


def _normalize_money_value(raw_value: str) -> str | None:
    compact_value = re.sub(r"[ \u00a0\u202f]", "", raw_value)
    compact_value = compact_value.replace(",", ".")

    if "." not in compact_value:
        compact_value = f"{compact_value}.00"

    try:
        money_value = Decimal(compact_value)
    except InvalidOperation:
        return None

    return f"{money_value:.2f}"


def _money_to_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _find_money_values(fragment: str) -> list[tuple[str, Decimal]]:
    values: list[tuple[str, Decimal]] = []

    for match in MONEY_RE.finditer(fragment):
        normalized_value = _normalize_money_value(match.group("amount"))
        decimal_value = _money_to_decimal(normalized_value)
        if normalized_value is not None and decimal_value is not None:
            values.append((normalized_value, decimal_value))

    return values


def _select_money_in_fragment(fragment: str, strategy: str = "first") -> str | None:
    values = _find_money_values(fragment)
    if not values:
        return None

    if strategy == "largest":
        return max(values, key=lambda item: item[1])[0]

    if strategy == "smallest":
        return min(values, key=lambda item: item[1])[0]

    return values[0][0]


def _is_excluded_amount_context(fragment: str) -> bool:
    return bool(EXCLUDED_AMOUNT_CONTEXT_RE.search(fragment))


def _find_explicit_amount(
    text: str,
    pattern: re.Pattern,
    excluded_context: bool = True,
    strategy: str = "first",
) -> tuple[str, str] | None:
    for match in pattern.finditer(text):
        fragment = re.sub(r"\s+", " ", match.group(0)).strip()
        if excluded_context and _is_excluded_amount_context(fragment):
            continue

        value = _select_money_in_fragment(fragment, strategy)
        if value is not None:
            return value, fragment

    return None


def _make_amount_field(
    name: str,
    label: str,
    value: str,
    confidence: float,
    source_text: str,
) -> ExtractedField:
    return ExtractedField(
        name=name,
        label=label,
        value=value,
        confidence=confidence,
        method="regex",
        source_text=source_text,
        warnings=[],
    )


def _iter_total_lines(text: str):
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        clean_line = re.sub(r"\s+", " ", line).strip()
        if not clean_line:
            continue
        if re.search(r"\bитого\b", clean_line, re.IGNORECASE):
            yield clean_line


def _find_amounts_in_total_line(text: str) -> tuple[str, str, str] | None:
    for line in _iter_total_lines(text):
        if _is_excluded_amount_context(line):
            continue

        values = _find_money_values(line)
        if len(values) < 2:
            continue

        sorted_values = sorted(values, key=lambda item: item[1], reverse=True)
        insured_amount = sorted_values[0][0]
        premium = sorted_values[-1][0]

        if sorted_values[0][1] > sorted_values[-1][1]:
            return insured_amount, premium, line

    return None


def _find_largest_money_as_insured_amount(text: str, premium_value: str | None) -> tuple[str, str] | None:
    candidates: list[tuple[str, Decimal, str]] = []
    premium_decimal = _money_to_decimal(premium_value)

    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        clean_line = re.sub(r"\s+", " ", line).strip()
        if not clean_line or _is_excluded_amount_context(clean_line):
            continue

        for match in MONEY_RE.finditer(clean_line):
            normalized_value = _normalize_money_value(match.group("amount"))
            decimal_value = _money_to_decimal(normalized_value)
            if normalized_value is None or decimal_value is None:
                continue

            amount_context = clean_line[max(0, match.start() - 20) : match.end() + 20]
            if "%" in amount_context or decimal_value < Decimal("1000.00"):
                continue

            if premium_decimal is not None and decimal_value <= premium_decimal:
                continue
            candidates.append((normalized_value, decimal_value, clean_line))

    if not candidates:
        return None

    value, _, source_text = max(candidates, key=lambda item: item[1])
    return value, source_text


def _iter_pledge_windows(text: str):
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    for match in PLEDGE_CONTEXT_RE.finditer(normalized_text):
        start = max(0, match.start() - 120)
        end = min(len(normalized_text), match.end() + 420)
        window = normalized_text[start:end]

        if CREDIT_CONTEXT_RE.search(window) and not PLEDGE_CONTEXT_RE.search(window):
            continue

        yield re.sub(r"\s+", " ", window).strip()


def _clean_pledge_number(value: str) -> str:
    return value.strip(" .,;:()[]")


def _is_more_specific_pledge_number(candidate: str, existing: str) -> bool:
    return candidate.startswith(f"{existing}-") or candidate.startswith(f"{existing}/")


def _is_less_specific_pledge_number(candidate: str, existing: str) -> bool:
    return existing.startswith(f"{candidate}-") or existing.startswith(f"{candidate}/")


def _make_inn_field(name: str, label: str, value: str, source_text: str) -> ExtractedField:
    return ExtractedField(
        name=name,
        label=label,
        value=value,
        confidence=0.85,
        method="regex",
        source_text=source_text,
        warnings=[],
    )


def _find_inn_near_role(text: str, role_pattern: re.Pattern) -> tuple[str, str] | None:
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    for role_match in role_pattern.finditer(normalized_text):
        start = max(0, role_match.start() - 80)
        end = min(len(normalized_text), role_match.end() + 260)
        source_text = re.sub(r"\s+", " ", normalized_text[start:end]).strip()
        after_role_text = normalized_text[role_match.end() : end]
        inn_match = INN_RE.search(after_role_text)
        if not inn_match:
            inn_match = INN_RE.search(source_text)
        if inn_match:
            return inn_match.group(1), source_text

    return None


def extract_contract_number(text: str) -> ExtractedField:
    """Extract an insurance contract or policy number from the document start."""
    fallback_field: ExtractedField | None = None

    for fragment in _iter_fragments(text):
        for match in NO_SIGN_RE.finditer(fragment):
            number_sign_position = match.end()

            if _is_excluded_context(fragment, match.start()):
                continue

            contract_number = _extract_number_after_sign(fragment, number_sign_position)
            if not contract_number:
                continue

            source_text = _make_source_text(fragment, match.start())

            if _has_insurance_label(fragment, match.start()):
                return ExtractedField(
                    name=CONTRACT_NUMBER_NAME,
                    label=CONTRACT_NUMBER_LABEL,
                    value=contract_number,
                    confidence=0.95,
                    method="regex",
                    source_text=source_text,
                    warnings=[],
                )

            if fallback_field is None:
                fallback_field = ExtractedField(
                    name=CONTRACT_NUMBER_NAME,
                    label=CONTRACT_NUMBER_LABEL,
                    value=contract_number,
                    confidence=0.75,
                    method="regex",
                    source_text=source_text,
                    warnings=[],
                )

    return fallback_field or _not_found_contract_number()


def extract_contract_date(text: str) -> ExtractedField:
    """Extract the contract or policy date from the document start."""
    limited_text = text[:DATE_SEARCH_LIMIT].replace("\r\n", "\n").replace("\r", "\n")

    for match in DATE_TEXT_RE.finditer(limited_text):
        if _is_excluded_date_context(limited_text, match.start()):
            continue

        day = int(match.group("day"))
        if not 1 <= day <= 31:
            continue

        month = MONTHS[match.group("month").lower()]
        year = match.group("year")
        value = f"{day:02d}.{month}.{year}"

        return ExtractedField(
            name=CONTRACT_DATE_NAME,
            label=CONTRACT_DATE_LABEL,
            value=value,
            confidence=0.9,
            method="regex",
            source_text=_make_source_text(limited_text, match.start()),
            warnings=[],
        )

    return _not_found_contract_date()


def extract_insurance_period(text: str) -> tuple[ExtractedField, ExtractedField]:
    """Extract insurance period start and end dates."""
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    for marker_match in PERIOD_MARKER_RE.finditer(normalized_text):
        segment_start = max(0, marker_match.start() - 180)
        segment = normalized_text[segment_start : marker_match.start() + 1000]
        marker_text = marker_match.group(0)

        if marker_text.lower() != "период страхования" and _is_excluded_period_context(segment[:250]):
            continue

        extracted_period = _extract_period_from_segment(segment)
        if extracted_period:
            start_value, end_value, source_text = extracted_period
            if marker_text not in source_text:
                source_text = f"{marker_text} {source_text}"
            return _make_period_fields(start_value, end_value, 0.95, source_text)

    extracted_period = _extract_period_from_segment(normalized_text)
    if extracted_period:
        start_value, end_value, source_text = extracted_period
        return _make_period_fields(start_value, end_value, 0.75, source_text)

    return _not_found_period_start(), _not_found_period_end()


def extract_amounts(text: str) -> dict[str, ExtractedField]:
    """Extract total insured amount and total insurance premium."""
    insured_amount_match = _find_explicit_amount(text, EXPLICIT_INSURED_AMOUNT_RE, strategy="largest")
    premium_match = _find_explicit_amount(text, EXPLICIT_PREMIUM_RE, strategy="smallest")
    insured_amount_confidence = 0.95
    premium_confidence = 0.95

    if insured_amount_match is None:
        insured_amount_match = _find_explicit_amount(text, SOFT_INSURED_AMOUNT_RE, strategy="largest")
        insured_amount_confidence = 0.85

    if premium_match is None:
        premium_match = _find_explicit_amount(text, SOFT_PREMIUM_RE, strategy="smallest")
        premium_confidence = 0.85

    if insured_amount_match is None or premium_match is None:
        total_line_match = _find_amounts_in_total_line(text)
        if total_line_match:
            insured_amount_from_total, premium_from_total, source_text = total_line_match

            if insured_amount_match is None:
                insured_amount_match = insured_amount_from_total, source_text
                insured_amount_confidence = 0.75

            if premium_match is None:
                premium_match = premium_from_total, source_text
                premium_confidence = 0.75

    if insured_amount_match is None:
        premium_value = premium_match[0] if premium_match else None
        largest_amount_match = _find_largest_money_as_insured_amount(text, premium_value)
        if largest_amount_match:
            insured_amount_match = largest_amount_match
            insured_amount_confidence = 0.6

    insured_amount_field = _not_found_total_insured_amount()
    premium_field = _not_found_total_insurance_premium()

    if insured_amount_match:
        insured_amount_field = _make_amount_field(
            TOTAL_INSURED_AMOUNT_NAME,
            TOTAL_INSURED_AMOUNT_LABEL,
            insured_amount_match[0],
            insured_amount_confidence,
            insured_amount_match[1],
        )

    if premium_match:
        premium_field = _make_amount_field(
            TOTAL_INSURANCE_PREMIUM_NAME,
            TOTAL_INSURANCE_PREMIUM_LABEL,
            premium_match[0],
            premium_confidence,
            premium_match[1],
        )

    insured_decimal = _money_to_decimal(insured_amount_field.value)
    premium_decimal = _money_to_decimal(premium_field.value)
    if insured_decimal is not None and premium_decimal is not None and insured_decimal <= premium_decimal:
        insured_amount_field.warnings.append("Страховая сумма не больше страховой премии.")
        premium_field.warnings.append("Страховая премия не меньше страховой суммы.")

    return {
        TOTAL_INSURED_AMOUNT_NAME: insured_amount_field,
        TOTAL_INSURANCE_PREMIUM_NAME: premium_field,
    }


def extract_pledge_agreements(text: str) -> list[ExtractedField]:
    """Extract pledge and mortgage agreement numbers in reading order."""
    fields: list[ExtractedField] = []
    seen_numbers: set[str] = set()

    for source_text in _iter_pledge_windows(text):
        if CREDIT_CONTEXT_RE.search(source_text) and not PLEDGE_CONTEXT_RE.search(source_text):
            continue

        for match in PLEDGE_NUMBER_RE.finditer(source_text):
            value = _clean_pledge_number(match.group(1))
            if value in seen_numbers:
                continue

            should_skip = False
            for index, existing_field in enumerate(fields):
                existing_value = existing_field.value or ""

                if _is_less_specific_pledge_number(value, existing_value):
                    should_skip = True
                    break

                if _is_more_specific_pledge_number(value, existing_value):
                    seen_numbers.discard(existing_value)
                    seen_numbers.add(value)
                    fields[index] = ExtractedField(
                        name=PLEDGE_AGREEMENT_NAME,
                        label=PLEDGE_AGREEMENT_LABEL,
                        value=value,
                        confidence=0.9,
                        method="regex",
                        source_text=source_text,
                        warnings=[],
                    )
                    should_skip = True
                    break

            if should_skip:
                continue

            seen_numbers.add(value)
            fields.append(
                ExtractedField(
                    name=PLEDGE_AGREEMENT_NAME,
                    label=PLEDGE_AGREEMENT_LABEL,
                    value=value,
                    confidence=0.9,
                    method="regex",
                    source_text=source_text,
                    warnings=[],
                )
            )

    return fields


def extract_inn_roles(text: str) -> dict[str, ExtractedField]:
    """Extract insurer and policyholder INN values by nearby role labels."""
    insurer_match = _find_inn_near_role(text, INSURER_CONTEXT_RE)
    policyholder_match = _find_inn_near_role(text, POLICYHOLDER_CONTEXT_RE)

    insurer_field = _not_found_insurer_inn()
    policyholder_field = _not_found_policyholder_inn()

    if insurer_match:
        insurer_field = _make_inn_field(
            INSURER_INN_NAME,
            INSURER_INN_LABEL,
            insurer_match[0],
            insurer_match[1],
        )

    if policyholder_match:
        policyholder_field = _make_inn_field(
            POLICYHOLDER_INN_NAME,
            POLICYHOLDER_INN_LABEL,
            policyholder_match[0],
            policyholder_match[1],
        )

    return {
        INSURER_INN_NAME: insurer_field,
        POLICYHOLDER_INN_NAME: policyholder_field,
    }


def extract_all_fields(text: str) -> ExtractionResult:
    """Run all regex extractors and return a validated extraction result."""
    contract_number = extract_contract_number(text)
    contract_date = extract_contract_date(text)
    period_start, period_end = extract_insurance_period(text)
    inn_roles = extract_inn_roles(text)
    amounts = extract_amounts(text)
    pledge_agreements = extract_pledge_agreements(text)

    result = ExtractionResult(
        contract_number=contract_number,
        contract_date=contract_date,
        period_start=period_start,
        period_end=period_end,
        insurer_inn=inn_roles[INSURER_INN_NAME],
        policyholder_inn=inn_roles[POLICYHOLDER_INN_NAME],
        total_insurance_premium=amounts[TOTAL_INSURANCE_PREMIUM_NAME],
        total_insured_amount=amounts[TOTAL_INSURED_AMOUNT_NAME],
        pledge_agreements=pledge_agreements,
    )
    validate_extraction_result(result)
    return result


def extract_insurance_fields(text: str) -> dict[str, str]:
    """Placeholder for the next stage of the diploma project.

    Later this service can combine regular expressions and NLP/LLM methods.
    For the first MVP, structured field extraction is intentionally disabled.
    """
    return {}
