from pathlib import Path

SUPPORTED_FORMATS = {
    ".txt",
    ".docx",
    ".pdf",
    ".csv",
    ".xlsx",
    ".json",
    ".xml",
    ".html",
    ".eml",
    ".vcf",
    ".ics",
    ".log",
    ".jpg",
    ".jpeg",
    ".png",
    ".wav",
    ".srt",
    ".kml",
    ".geojson",
    ".sql",
    ".mp4",
}


def scan_directory(root_path: str):
    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {root}")

    files = []

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS:
            files.append(
                {
                    "path": str(path),
                    "relative_path": str(path.relative_to(root)),
                    "format": path.suffix.lower(),
                    "bytes": path.stat().st_size,
                }
            )

    return sorted(files, key=lambda item: item["relative_path"])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m ingestion.extractors.file_scanner <dataset_path>")
        raise SystemExit(1)

    dataset_path = sys.argv[1]
    results = scan_directory(dataset_path)

    print(f"Found {len(results)} supported files.")

    for item in results:
        print(
            f"{item['format']:8} "
            f"{item['bytes']:8} bytes  "
            f"{item['relative_path']}"
        )