import sys
from pathlib import Path

from app.services.docx_parser import parse_docx


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python debug_parse_docx.py path/to/document.docx")
        return 1

    file_path = Path(sys.argv[1])
    parsed_document = parse_docx(file_path)

    print(parsed_document.full_text[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
