import re


_QUOTE_TRANSLATION = str.maketrans(
    {
        "\u00ab": '"',
        "\u00bb": '"',
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
    }
)

_NBSP_CHARS = "\u00a0\u202f\u2007"
_DATE_PATTERN = re.compile(
    r"(?<![A-Za-zА-Яа-яЁё0-9№/.-])"
    r"(\d{1,2})\s*([./-])\s*(\d{1,2})\s*([./-])\s*(\d{2,4})"
    r"(?![A-Za-zА-Яа-яЁё0-9/.-])"
)


def normalize_quotes(text: str) -> str:
    """Convert common quote styles to regular double quotes."""
    return text.translate(_QUOTE_TRANSLATION)


def normalize_spaces(text: str) -> str:
    """Normalize whitespace while keeping paragraph boundaries readable."""
    for char in _NBSP_CHARS:
        text = text.replace(char, " ")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    normalized_lines: list[str] = []
    previous_line_was_empty = False

    for line in text.split("\n"):
        # Collapse only horizontal whitespace inside a line. Newlines are
        # handled separately so paragraphs from DOCX/PDF do not merge together.
        line = re.sub(r"[ \t\f\v]+", " ", line).strip()

        if not line:
            if normalized_lines and not previous_line_was_empty:
                normalized_lines.append("")
            previous_line_was_empty = True
            continue

        normalized_lines.append(line)
        previous_line_was_empty = False

    return "\n".join(normalized_lines).strip()


def normalize_dates_text(text: str) -> str:
    """Normalize simple numeric dates without touching contract numbers."""

    def replace_date(match: re.Match) -> str:
        day = int(match.group(1))
        month = int(match.group(3))
        year = match.group(5)

        if not 1 <= day <= 31 or not 1 <= month <= 12:
            return match.group(0)

        return f"{day:02d}.{month:02d}.{year}"

    return _DATE_PATTERN.sub(replace_date, text)


def normalize_text(text: str) -> str:
    """Run all text normalization steps used before storing extracted text."""
    text = normalize_quotes(text)
    text = normalize_spaces(text)
    text = normalize_dates_text(text)
    return normalize_spaces(text)
