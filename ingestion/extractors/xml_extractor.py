from pathlib import Path
import xml.etree.ElementTree as ET


def extract_xml(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if path.suffix.lower() != ".xml":
        raise ValueError(f"Expected .xml file, got {path.suffix}")

    tree = ET.parse(path)
    root = tree.getroot()

    return root


def element_to_dict(element):
    result = {}

    if element.attrib:
        result["@attributes"] = dict(element.attrib)

    children = list(element)

    if children:
        grouped = {}

        for child in children:
            child_data = element_to_dict(child)

            if child.tag in grouped:
                if not isinstance(grouped[child.tag], list):
                    grouped[child.tag] = [grouped[child.tag]]
                grouped[child.tag].append(child_data)
            else:
                grouped[child.tag] = child_data

        result.update(grouped)

    text = (element.text or "").strip()

    if text:
        if result:
            result["#text"] = text
        else:
            return text

    return result


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print(
            "Usage: python -m ingestion.extractors.xml_extractor <file>"
        )
        raise SystemExit(1)

    root = extract_xml(sys.argv[1])

    print(f"Root element: {root.tag}")

    print("\n--- CONTENT ---")
    pprint(element_to_dict(root))