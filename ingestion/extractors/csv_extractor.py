from pathlib import Path
import csv


def extract_csv(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected .csv file, got {path.suffix}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.csv_extractor <file>"
        )
        raise SystemExit(1)

    rows = extract_csv(sys.argv[1])

    print(f"Extracted {len(rows)} rows.")

    if rows:
        print("\n--- COLUMNS ---")
        print(", ".join(rows[0].keys()))

        print("\n--- FIRST ROW ---")
        print(rows[0])