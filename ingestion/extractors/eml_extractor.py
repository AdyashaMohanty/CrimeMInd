from pathlib import Path
from email import policy
from email.parser import BytesParser


def extract_eml(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".eml":
        raise ValueError(f"Expected .eml file, got {path.suffix}")

    with open(path, "rb") as f:
        message = BytesParser(policy=policy.default).parse(f)

    return {
        "from": message.get("From"),
        "to": message.get("To"),
        "cc": message.get("Cc"),
        "subject": message.get("Subject"),
        "date": message.get("Date"),
        "body": get_body(message),
    }


def get_body(message):
    if message.is_multipart():
        parts = []

        for part in message.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_content())

        return "\n".join(parts).strip()

    return message.get_content()


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.eml_extractor <file>"
        )
        raise SystemExit(1)

    result = extract_eml(sys.argv[1])

    print("--- EMAIL ---")
    pprint(result)