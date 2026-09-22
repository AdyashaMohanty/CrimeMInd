from pathlib import Path
import pandas as pd
import json
from collections import Counter

ROOT = Path(r".\data\raw\CrimeMind_Synthetic_World_v2")

errors = []
warnings = []


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def read_csv(relative_path):
    path = ROOT / relative_path

    if not path.exists():
        errors.append(f"Missing file: {relative_path}")
        print(f"✗ {relative_path} — MISSING")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
        print(f"✓ {relative_path} — {len(df)} rows")
        return df
    except Exception as e:
        errors.append(f"Cannot read {relative_path}: {e}")
        print(f"✗ {relative_path} — {e}")
        return pd.DataFrame()


def check_unique(df, column, name):
    if column not in df.columns:
        errors.append(f"{name}: missing column {column}")
        return

    nulls = int(df[column].isna().sum())
    duplicates = int(df[column].dropna().duplicated().sum())

    print(f"  {column}: null={nulls}, duplicates={duplicates}")

    if nulls:
        errors.append(f"{name}.{column}: {nulls} null values")

    if duplicates:
        errors.append(f"{name}.{column}: {duplicates} duplicate values")


def check_reference(df, column, valid_ids, name):
    if column not in df.columns:
        return

    values = set(df[column].dropna().astype(str))
    invalid = sorted(values - valid_ids)

    print(
        f"  {name}.{column}: "
        f"values={len(values)}, invalid={len(invalid)}"
    )

    if invalid:
        warnings.append(
            f"{name}.{column}: invalid references "
            f"{invalid[:10]}"
        )


# ============================================================================
# 1. ROOT
# ============================================================================

section("1. ROOT STRUCTURE")

if not ROOT.exists():
    raise SystemExit(
        f"ERROR: synthetic world not found:\n{ROOT.resolve()}"
    )

print("Root:", ROOT.resolve())

required_dirs = [
    "00_CASE_CONTEXT",
    "01_PEOPLE",
    "02_LOCATIONS",
    "03_COMMUNICATIONS",
    "04_FINANCIAL",
    "05_VEHICLES",
    "06_DEVICES",
    "07_ACCESS_SECURITY",
    "08_CCTV",
    "09_AUDIO",
    "10_FORENSICS",
    "11_LEGAL_BUSINESS",
    "12_PUBLIC_INFORMATION",
    "13_INVESTIGATION_MATERIAL",
    "14_EVALUATION_ONLY",
    "15_RAW_SOURCE",
    "16_NORMALIZATION_REFERENCE",
]

for directory in required_dirs:
    path = ROOT / directory

    if path.exists():
        print(f"✓ {directory}")
    else:
        print(f"✗ {directory}")
        errors.append(f"Missing directory: {directory}")


# ============================================================================
# 2. MANIFEST / CASE CONTEXT
# ============================================================================

section("2. MANIFEST AND CASE CONTEXT")

manifest = ROOT / "MANIFEST.json"

if manifest.exists():
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        print("✓ MANIFEST.json is valid JSON")
        print("  Manifest keys:", list(data.keys()))
    except Exception as e:
        errors.append(f"Invalid MANIFEST.json: {e}")
else:
    errors.append("Missing MANIFEST.json")

for filename in [
    "00_CASE_CONTEXT/case_overview.md",
    "00_CASE_CONTEXT/city_profile.md",
]:
    path = ROOT / filename

    if path.exists():
        text = path.read_text(encoding="utf-8", errors="replace")
        print(f"✓ {filename} — {len(text)} characters")
    else:
        errors.append(f"Missing case file: {filename}")


# ============================================================================
# 3. LOAD DATASETS
# ============================================================================

section("3. DATASET INVENTORY")

people = read_csv(
    "01_PEOPLE/person_profiles/people.csv"
)

locations = read_csv(
    "02_LOCATIONS/locations.csv"
)

relationships = read_csv(
    "01_PEOPLE/relationships/relationships.csv"
)

vehicles = read_csv(
    "05_VEHICLES/registry/vehicles.csv"
)

vehicle_sightings = read_csv(
    "05_VEHICLES/sightings/vehicle_sightings.csv"
)

calls = read_csv(
    "03_COMMUNICATIONS/calls/calls.csv"
)

messages = read_csv(
    "03_COMMUNICATIONS/messages/messages.csv"
)

emails = read_csv(
    "03_COMMUNICATIONS/emails/emails.csv"
)

transactions = read_csv(
    "04_FINANCIAL/transactions/transactions.csv"
)

gps = read_csv(
    "06_DEVICES/gps/gps_logs.csv"
)

gps_full = read_csv(
    "06_DEVICES/gps/gps_logs_full.csv"
)

browser = read_csv(
    "06_DEVICES/browser/browser_history.csv"
)

access = read_csv(
    "07_ACCESS_SECURITY/access_logs/access_logs.csv"
)

visitors = read_csv(
    "07_ACCESS_SECURITY/visitor_logs/visitor_logs.csv"
)

cameras = read_csv(
    "08_CCTV/metadata/cameras.csv"
)

cctv = read_csv(
    "08_CCTV/annotations/cctv_annotations.csv"
)

audio = read_csv(
    "09_AUDIO/recordings/audio_metadata.csv"
)

forensics = read_csv(
    "10_FORENSICS/reports/forensic_reports.csv"
)

contradictions = read_csv(
    "13_INVESTIGATION_MATERIAL/contradiction_register/contradictions.csv"
)


# ============================================================================
# 4. ID INTEGRITY
# ============================================================================

section("4. ID INTEGRITY")

people_ids = set(
    people["person_id"].dropna().astype(str)
) if "person_id" in people else set()

location_ids = set(
    locations["location_id"].dropna().astype(str)
) if "location_id" in locations else set()

vehicle_ids = set(
    vehicles["vehicle_id"].dropna().astype(str)
) if "vehicle_id" in vehicles else set()

print("People:", len(people_ids))
print("Locations:", len(location_ids))
print("Vehicles:", len(vehicle_ids))

check_unique(people, "person_id", "people")
check_unique(locations, "location_id", "locations")
check_unique(vehicles, "vehicle_id", "vehicles")


# ============================================================================
# 5. PEOPLE → LOCATIONS / VEHICLES
# ============================================================================

section("5. PEOPLE REFERENCES")

check_reference(
    people,
    "residence_location_id",
    location_ids,
    "people"
)

check_reference(
    people,
    "work_location_id",
    location_ids,
    "people"
)

if "owner_person_id" in vehicles.columns:
    check_reference(
        vehicles,
        "owner_person_id",
        people_ids,
        "vehicles"
    )

print(
    "vehicle_owned values:",
    sorted(
        people["vehicle_owned"]
        .dropna()
        .astype(str)
        .unique()
    ) if "vehicle_owned" in people else []
)


# ============================================================================
# 6. RELATIONSHIPS
# ============================================================================

section("6. PEOPLE RELATIONSHIPS")

print("Columns:", relationships.columns.tolist())

for column in relationships.columns:

    lower = column.lower()

    if "person" in lower or "entity" in lower:

        values = set(
            relationships[column]
            .dropna()
            .astype(str)
        )

        invalid = values - people_ids

        print(
            f"  {column}: "
            f"values={len(values)}, "
            f"invalid={len(invalid)}"
        )

        if invalid:
            warnings.append(
                f"relationships.{column}: "
                f"invalid references {sorted(invalid)[:10]}"
            )


# ============================================================================
# 7. VEHICLE SIGHTINGS
# ============================================================================

section("7. VEHICLE SIGHTINGS")

check_reference(
    vehicle_sightings,
    "vehicle_id",
    vehicle_ids,
    "vehicle_sightings"
)

check_reference(
    vehicle_sightings,
    "location_id",
    location_ids,
    "vehicle_sightings"
)


# ============================================================================
# 8. COMMUNICATIONS
# ============================================================================

section("8. COMMUNICATIONS")

for df, name in [
    (calls, "calls"),
    (messages, "messages"),
    (emails, "emails"),
]:

    print(f"\n{name}")
    print("Columns:", df.columns.tolist())

    for column in df.columns:

        lower = column.lower()

        if (
            "person" in lower
            or "sender" in lower
            or "receiver" in lower
        ):

            values = set(
                df[column]
                .dropna()
                .astype(str)
            )

            invalid = values - people_ids

            print(
                f"  {column}: "
                f"values={len(values)}, "
                f"unmatched={len(invalid)}"
            )

            if invalid:
                warnings.append(
                    f"{name}.{column}: "
                    f"unmatched values {sorted(invalid)[:10]}"
                )


# ============================================================================
# 9. TRANSACTIONS
# ============================================================================

section("9. FINANCIAL TRANSACTIONS")

print("Columns:", transactions.columns.tolist())

for column in transactions.columns:

    lower = column.lower()

    if (
        "person" in lower
        or "sender" in lower
        or "receiver" in lower
    ):

        values = set(
            transactions[column]
            .dropna()
            .astype(str)
        )

        invalid = values - people_ids

        print(
            f"  {column}: "
            f"values={len(values)}, "
            f"unmatched={len(invalid)}"
        )

        if invalid:
            warnings.append(
                f"transactions.{column}: "
                f"unmatched values {sorted(invalid)[:10]}"
            )

if "amount" in transactions.columns:

    amounts = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    print("Invalid amounts:", int(amounts.isna().sum()))
    print("Zero/negative amounts:", int((amounts <= 0).sum()))


# ============================================================================
# 10. GPS
# ============================================================================

section("10. GPS DATA")

for df, name in [
    (gps, "gps_logs"),
    (gps_full, "gps_logs_full"),
]:

    print(f"\n{name}")
    print("Columns:", df.columns.tolist())

    for column in df.columns:

        lower = column.lower()

        values = set(
            df[column]
            .dropna()
            .astype(str)
        )

        if "person" in lower:

            invalid = values - people_ids

            print(
                f"  {column}: "
                f"unmatched people={len(invalid)}"
            )

        if "location" in lower:

            invalid = values - location_ids

            print(
                f"  {column}: "
                f"unmatched locations={len(invalid)}"
            )


# ============================================================================
# 11. ACCESS / VISITOR LOGS
# ============================================================================

section("11. ACCESS AND VISITOR LOGS")

for df, name in [
    (access, "access_logs"),
    (visitors, "visitor_logs"),
]:

    print(f"\n{name}")
    print("Columns:", df.columns.tolist())

    for column in df.columns:

        lower = column.lower()

        values = set(
            df[column]
            .dropna()
            .astype(str)
        )

        if "person" in lower:

            invalid = values - people_ids

            print(
                f"  {column}: "
                f"unmatched people={len(invalid)}"
            )

        if "location" in lower:

            invalid = values - location_ids

            print(
                f"  {column}: "
                f"unmatched locations={len(invalid)}"
            )


# ============================================================================
# 12. CCTV
# ============================================================================

section("12. CCTV")

print("Camera columns:", cameras.columns.tolist())
print("Annotation columns:", cctv.columns.tolist())

if (
    "camera_id" in cameras.columns
    and "camera_id" in cctv.columns
):

    camera_ids = set(
        cameras["camera_id"]
        .dropna()
        .astype(str)
    )

    check_reference(
        cctv,
        "camera_id",
        camera_ids,
        "cctv"
    )

for column in cctv.columns:

    lower = column.lower()

    if "person" in lower:

        values = set(
            cctv[column]
            .dropna()
            .astype(str)
        )

        invalid = values - people_ids

        print(
            f"  {column}: "
            f"unmatched people={len(invalid)}"
        )

    if "vehicle" in lower:

        values = set(
            cctv[column]
            .dropna()
            .astype(str)
        )

        invalid = values - vehicle_ids

        print(
            f"  {column}: "
            f"unmatched vehicles={len(invalid)}"
        )

frame_dir = ROOT / "08_CCTV/frames"

if frame_dir.exists():

    frames = [
        p for p in frame_dir.iterdir()
        if p.is_file()
    ]

    print("CCTV frame files:", len(frames))


# ============================================================================
# 13. AUDIO
# ============================================================================

section("13. AUDIO")

wav_dir = ROOT / "09_AUDIO/recordings/wav"
transcript_dir = ROOT / "09_AUDIO/transcripts"

wav_files = (
    list(wav_dir.glob("*.wav"))
    if wav_dir.exists()
    else []
)

transcript_files = (
    list(transcript_dir.glob("*_transcript.txt"))
    if transcript_dir.exists()
    else []
)

print("Audio metadata rows:", len(audio))
print("WAV files:", len(wav_files))
print("Transcript files:", len(transcript_files))


# ============================================================================
# 14. OTHER MATERIAL
# ============================================================================

section("14. OTHER SOURCE MATERIAL")

directories = [
    "01_PEOPLE/interviews",
    "10_FORENSICS/reports",
    "11_LEGAL_BUSINESS/employment",
    "11_LEGAL_BUSINESS/invoices",
    "11_LEGAL_BUSINESS/leases",
    "12_PUBLIC_INFORMATION/news",
    "12_PUBLIC_INFORMATION/public_posts",
    "13_INVESTIGATION_MATERIAL/evidence_requests",
    "13_INVESTIGATION_MATERIAL/investigator_notes",
]

for directory in directories:

    path = ROOT / directory

    files = (
        [p for p in path.iterdir() if p.is_file()]
        if path.exists()
        else []
    )

    print(f"{directory}: {len(files)} files")

print("Forensic records:", len(forensics))
print("Contradiction records:", len(contradictions))


# ============================================================================
# 15. DATE/TIME SANITY
# ============================================================================

section("15. DATE / TIME SANITY")

for df, name in [
    (calls, "calls"),
    (messages, "messages"),
    (emails, "emails"),
    (transactions, "transactions"),
    (vehicle_sightings, "vehicle_sightings"),
    (gps, "gps"),
    (gps_full, "gps_full"),
    (access, "access"),
    (visitors, "visitors"),
    (cctv, "cctv"),
]:

    invalid_total = 0

    for column in df.columns:

        lower = column.lower()

        if any(
            keyword in lower
            for keyword in [
                "time",
                "date",
                "timestamp",
                "observed"
            ]
        ):

            original = df[column]

            parsed = pd.to_datetime(
                original,
                errors="coerce"
            )

            invalid = (
                parsed.isna()
                & original.notna()
            ).sum()

            invalid_total += int(invalid)

    print(
        f"{name}: invalid timestamps={invalid_total}"
    )

    if invalid_total:
        warnings.append(
            f"{name}: {invalid_total} invalid timestamp values"
        )


# ============================================================================
# 16. DATASET QUALITY
# ============================================================================

section("16. DATASET QUALITY")

datasets = [
    (people, "people"),
    (locations, "locations"),
    (relationships, "relationships"),
    (vehicles, "vehicles"),
    (vehicle_sightings, "vehicle_sightings"),
    (calls, "calls"),
    (messages, "messages"),
    (emails, "emails"),
    (transactions, "transactions"),
    (gps, "gps"),
    (gps_full, "gps_full"),
    (browser, "browser"),
    (access, "access"),
    (visitors, "visitors"),
    (cameras, "cameras"),
    (cctv, "cctv"),
    (audio, "audio"),
    (forensics, "forensics"),
    (contradictions, "contradictions"),
]

for df, name in datasets:

    if df.empty:
        print(f"{name}: EMPTY")
        continue

    print(
        f"{name}: "
        f"rows={len(df)}, "
        f"columns={len(df.columns)}, "
        f"duplicate_rows={int(df.duplicated().sum())}, "
        f"null_cells={int(df.isna().sum().sum())}"
    )


# ============================================================================
# 17. EVALUATION-ONLY
# ============================================================================

section("17. EVALUATION-ONLY ISOLATION")

evaluation_dir = ROOT / "14_EVALUATION_ONLY"

evaluation_files = (
    [p for p in evaluation_dir.rglob("*") if p.is_file()]
    if evaluation_dir.exists()
    else []
)

print("Evaluation-only files:", len(evaluation_files))

for path in evaluation_files:
    print(" ", path.relative_to(ROOT))

print()
print("RULE: 14_EVALUATION_ONLY must NOT be ingested.")


# ============================================================================
# 18. FILE INVENTORY
# ============================================================================

section("18. COMPLETE FILE INVENTORY")

all_files = [
    p for p in ROOT.rglob("*")
    if p.is_file()
]

print("Total files:", len(all_files))

extensions = Counter(
    p.suffix.lower()
    if p.suffix
    else "[no extension]"
    for p in all_files
)

for extension, count in sorted(extensions.items()):
    print(f"  {extension}: {count}")


# ============================================================================
# 19. FINAL RESULT
# ============================================================================

section("19. FINAL RESULT")

print("CRITICAL ERRORS:", len(errors))
print("WARNINGS:", len(warnings))

if errors:

    print("\nCRITICAL ERRORS")

    for error in errors:
        print("✗", error)

else:

    print("✓ No critical structural errors detected.")


if warnings:

    print("\nWARNINGS")

    for warning in warnings:
        print("!", warning)

else:

    print("✓ No warnings detected.")


print("\n" + "=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
print("No Oracle data was modified.")
print("No synthetic-world files were modified.")