import sys
from pathlib import Path

from app.services.pdf_parser import parse_pdf


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python debug_parse_pdf.py path/to/document.pdf")
        return 1

    file_path = Path(sys.argv[1])
    parsed_document = parse_pdf(str(file_path))

    if parsed_document.warning:
        print(f"WARNING: {parsed_document.warning}")

    print(parsed_document.full_text[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
