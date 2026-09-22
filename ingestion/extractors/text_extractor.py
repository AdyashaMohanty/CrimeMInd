from pathlib import Path


TEXT_EXTENSIONS = {
    ".txt",
    ".srt",
    ".log",
    ".sql",
    ".html",
    ".kml",
    ".geojson",
    ".json",
    ".xml",
    ".vcf",
    ".ics",
    ".eml",
}


def extract_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported text format: {path.suffix}")

    return path.read_text(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m ingestion.extractors.text_extractor <file>")
        raise SystemExit(1)

    file_path = sys.argv[1]

    text = extract_text(file_path)

    print(f"Extracted {len(text)} characters.")
    print("\n--- CONTENT ---")
    print(text)