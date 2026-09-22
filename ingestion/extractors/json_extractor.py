from pathlib import Path
import json


def extract_json(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".json":
        raise ValueError(f"Expected .json file, got {path.suffix}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.json_extractor <file>"
        )
        raise SystemExit(1)

    data = extract_json(sys.argv[1])

    print(f"Data type: {type(data).__name__}")

    if isinstance(data, list):
        print(f"Records: {len(data)}")
    elif isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")

    print("\n--- CONTENT ---")
    pprint(data)