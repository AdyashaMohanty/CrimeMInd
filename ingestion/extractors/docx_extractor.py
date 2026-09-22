from pathlib import Path
from docx import Document


def extract_docx(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".docx":
        raise ValueError(f"Expected .docx file, got {path.suffix}")

    # Try genuine DOCX first
    try:
        document = Document(path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception as exc:
        # Some synthetic-world files use .docx extension
        # but contain plain-text evidence.
        try:
            text = path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            raise RuntimeError(
                f"File is not a valid DOCX and is not UTF-8 text: {path}"
            ) from exc

        if not text:
            raise RuntimeError(
                f"File is neither a valid DOCX nor usable text: {path}"
            ) from exc

        print(
            f"WARNING: {path.name} is not a valid DOCX. "
            "Treating it as plain-text evidence."
        )

        return text


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.docx_extractor <file>"
        )
        raise SystemExit(1)

    file_path = sys.argv[1]
    text = extract_docx(file_path)

    print(f"Extracted {len(text)} characters.")
    print("\n--- CONTENT ---")
    print(text)