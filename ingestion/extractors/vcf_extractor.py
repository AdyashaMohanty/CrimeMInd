from pathlib import Path


def extract_vcf(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".vcf":
        raise ValueError(f"Expected .vcf file, got {path.suffix}")

    text = path.read_text(encoding="utf-8", errors="replace")

    contact = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        if key == "FN":
            contact["name"] = value
        elif key == "TEL":
            contact["phone"] = value
        elif key == "EMAIL":
            contact["email"] = value
        elif key == "ORG":
            contact["organization"] = value

    return contact


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.vcf_extractor <file>"
        )
        raise SystemExit(1)

    result = extract_vcf(sys.argv[1])

    print("--- CONTACT ---")
    pprint(result)