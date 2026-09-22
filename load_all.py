from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import re

import pandas as pd
import oracledb

# ============================================================
# CRIMEMIND - FULL SYNTHETIC WORLD INGESTION
# ============================================================
# Loads the complete operational synthetic world into Oracle.
#
# Existing Stage 1 and Stage 2 data are detected and reused;
# they are NOT duplicated.
#
# Evaluation-only data under 14_EVALUATION_ONLY is NEVER read.
#
# A single Oracle transaction is used for the full run:
#   - success -> COMMIT
#   - any error -> ROLLBACK
# ============================================================

ROOT = Path(r".\data\raw\CrimeMind_Synthetic_World_v2")
ORACLE_USER = "CRIMEMIND"
ORACLE_PASSWORD = "CrimeMind123"
ORACLE_DSN = "localhost:1521/XE"
ORACLE_CLIENT = r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
CASE_REFERENCE = "CM-2026-0314-NDP"
LOCAL_TZ = timezone(timedelta(hours=5, minutes=30))

oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT)
connection = oracledb.connect(
    user=ORACLE_USER,
    password=ORACLE_PASSWORD,
    dsn=ORACLE_DSN,
)

# External source ID -> Oracle numeric ID
entity_map = {}
location_map = {}
vehicle_map = {}

ENTITY_TYPES = {
    "PERSON": 1,
    "ORGANIZATION": 2,
    "ACCOUNT": 3,
    "DEVICE": 4,
    "UNKNOWN": 5,
}

RELATIONSHIP_TYPES = {
    "ASSOCIATE": 1,
    "FAMILY": 2,
    "BUSINESS": 3,
    "EMPLOYMENT": 4,
    "TENANCY": 5,
    "CONTACT": 6,
    "EMPLOYER_EMPLOYEE": 4,
    "LANDLORD_TENANT": 5,
    "FRIEND": 1,
    "FORMER_PARTNER": 1,
    "NEIGHBOR": 1,
    "PROFESSOR_STUDENT": 1,
    "FORMER_COWORKER": 1,
    "LAWYER_CLIENT": 3,
    "COMPETITOR": 3,
    "SERVICE_RELATIONSHIP": 3,
    "DEBT": 3,
    "DOCTOR_PATIENT": 3,
    "BUSINESS_PARTNER": 3,
}

EVENT_TYPES = {
    "INCIDENT": 1,
    "LOCATION_OBSERVATION": 2,
    "ACCESS": 3,
    "MOVEMENT": 4,
    "COMMUNICATION": 5,
    "TRANSACTION": 6,
    "ALARM": 7,
    "MEETING": 8,
    "OTHER": 9,
}

COMMUNICATION_TYPES = {
    "CALL": 1,
    "SMS": 2,
    "EMAIL": 3,
    "CHAT": 4,
    "OTHER": 5,
}

EVIDENCE_TYPES = {
    "CCTV": 1,
    "DNA": 2,
    "FINGERPRINT": 3,
    "GPS": 4,
    "ACCESS_LOG": 5,
    "FINANCIAL": 6,
    "COMMUNICATION": 7,
    "WITNESS": 8,
    "DIGITAL": 9,
    "DOCUMENT": 10,
}


def read_csv(relative_path):
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


def text(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def number(value):
    if pd.isna(value):
        return None
    return float(value)


def parse_time(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt


def json_clob(data):
    return json.dumps(data, ensure_ascii=False, default=str)


def execute_scalar(cursor, sql, binds=None):
    cursor.execute(sql, binds or {})
    row = cursor.fetchone()
    return None if row is None else row[0]


def insert_entity(cursor, external_reference, display_name, entity_type_id, attributes=None):
    # Old Oracle/python-oracledb compatibility: insert, then query by
    # external_reference rather than relying on RETURNING bind behavior.
    existing = execute_scalar(
        cursor,
        "SELECT entity_id FROM entities WHERE external_reference = :x",
        {"x": external_reference},
    )
    if existing is not None:
        return int(existing)

    cursor.execute(
        """
        INSERT INTO entities (
            entity_id, entity_type_id, display_name,
            external_reference, created_at
        )
        VALUES (
            SEQ_ENTITIES.NEXTVAL, :t, :n, :x, SYSTIMESTAMP
        )
        """,
        {
            "t": entity_type_id,
            "n": display_name[:200],
            "x": external_reference[:100],
        },
    )

    return int(execute_scalar(
        cursor,
        "SELECT entity_id FROM entities WHERE external_reference = :x",
        {"x": external_reference},
    ))


def ensure_case_link(cursor, table_name, id_column, case_id, row_id):
    exists = execute_scalar(
        cursor,
        f"SELECT COUNT(*) FROM {table_name} WHERE case_id = :c AND {id_column} = :r",
        {"c": case_id, "r": row_id},
    )
    if not exists:
        cursor.execute(
            f"INSERT INTO {table_name} (case_id, {id_column}) VALUES (:c, :r)",
            {"c": case_id, "r": row_id},
        )


def source_exists(cursor, table_name, source_reference):
    return bool(execute_scalar(
        cursor,
        f"SELECT COUNT(*) FROM {table_name} WHERE source_reference = :s",
        {"s": source_reference},
    ))


def load_case(cursor):
    case_id = execute_scalar(
        cursor,
        "SELECT case_id FROM investigation_cases WHERE case_reference = :r",
        {"r": CASE_REFERENCE},
    )
    if case_id is not None:
        return int(case_id)

    case_file = ROOT / "00_CASE_CONTEXT" / "case_overview.md"
    case_text = case_file.read_text(encoding="utf-8", errors="ignore")

    cursor.execute(
        """
        INSERT INTO investigation_cases (
            case_id, case_reference, title, opened_at,
            incident_time, status, metadata
        )
        VALUES (
            SEQ_INVESTIGATION_CASES.NEXTVAL,
            :r, :title, SYSTIMESTAMP,
            :incident_time, 'OPEN', :metadata
        )
        """,
        {
            "r": CASE_REFERENCE,
            "title": "The Green Park Warehouse Incident",
            "incident_time": parse_time("2026-03-14 21:47:00"),
            "metadata": json_clob({
                "city": "Nandipur",
                "country": "India",
                "reported_location_external_reference": "L011",
                "source_reference": "00_CASE_CONTEXT/case_overview.md",
                "estimated_incident_window": "21:40-21:55",
                "case_context": case_text,
            }),
        },
    )
    return int(execute_scalar(
        cursor,
        "SELECT case_id FROM investigation_cases WHERE case_reference = :r",
        {"r": CASE_REFERENCE},
    ))


def load_locations(cursor, case_id):
    df = read_csv("02_LOCATIONS/locations.csv")
    for _, row in df.iterrows():
        ext = text(row["location_id"])
        existing = execute_scalar(
            cursor,
            "SELECT location_id FROM locations WHERE external_reference = :x",
            {"x": ext},
        )
        if existing is None:
            cursor.execute(
                """
                INSERT INTO locations (
                    location_id, external_reference, location_name,
                    location_type, address, latitude, longitude,
                    created_at
                )
                VALUES (
                    SEQ_LOCATIONS.NEXTVAL, :x, :n, :t, :a,
                    :lat, :lon, SYSTIMESTAMP
                )
                """,
                {
                    "x": ext,
                    "n": text(row["name"]),
                    "t": text(row["type"]),
                    "a": text(row["address"]),
                    "lat": number(row["latitude"]),
                    "lon": number(row["longitude"]),
                },
            )
            existing = execute_scalar(
                cursor,
                "SELECT location_id FROM locations WHERE external_reference = :x",
                {"x": ext},
            )
        location_map[ext] = int(existing)
        ensure_case_link(cursor, "case_locations", "location_id", case_id, int(existing))


def load_people(cursor, case_id):
    df = read_csv("01_PEOPLE/person_profiles/people.csv")
    for _, row in df.iterrows():
        ext = text(row["person_id"])
        existing = execute_scalar(
            cursor,
            "SELECT entity_id FROM entities WHERE external_reference = :x",
            {"x": ext},
        )
        if existing is None:
            attrs = {
                "age": number(row["age"]),
                "occupation": text(row["occupation"]),
                "employer": text(row["employer"]),
                "residential_address": text(row["residential_address"]),
                "residence_location_id": text(row["residence_location_id"]),
                "phone_primary": text(row["phone_primary"]),
                "phone_secondary": text(row["phone_secondary"]),
                "email_primary": text(row["email_primary"]),
                "email_secondary": text(row["email_secondary"]),
                "work_location_id": text(row["work_location_id"]),
                "routine_type": text(row["routine_type"]),
                "source_file": "01_PEOPLE/person_profiles/people.csv",
            }
            cursor.execute(
                """
                INSERT INTO entities (
                    entity_id, entity_type_id, display_name,
                    external_reference, created_at
                )
                VALUES (
                    SEQ_ENTITIES.NEXTVAL, 1, :n, :x, SYSTIMESTAMP
                )
                """,
                {"n": text(row["full_name"]), "x": ext},
            )
            existing = execute_scalar(
                cursor,
                "SELECT entity_id FROM entities WHERE external_reference = :x",
                {"x": ext},
            )
            # Store person metadata in a separate JSON attribute is not
            # available on ENTITIES in this schema; source data remains
            # in the raw world and person identity is preserved by Pxxx.
        entity_map[ext] = int(existing)
        ensure_case_link(cursor, "case_entities", "entity_id", case_id, int(existing))


def load_vehicles(cursor, case_id):
    df = read_csv("05_VEHICLES/registry/vehicles.csv")
    for _, row in df.iterrows():
        ext = text(row["vehicle_id"])
        existing = execute_scalar(
            cursor,
            "SELECT vehicle_id FROM vehicles WHERE external_reference = :x",
            {"x": ext},
        )
        if existing is None:
            attrs = {
                "color": text(row["color"]),
                "registration_date": text(row["registration_date"]),
                "insurance_status": text(row["insurance_status"]),
                "owner_person_id": text(row["owner_person_id"]),
                "source_file": "05_VEHICLES/registry/vehicles.csv",
            }
            cursor.execute(
                """
                INSERT INTO vehicles (
                    vehicle_id, external_reference, vehicle_type,
                    make_model, registration_reference, attributes
                )
                VALUES (
                    SEQ_VEHICLES.NEXTVAL, :x, :vt, :mm, :reg, :attrs
                )
                """,
                {
                    "x": ext,
                    "vt": text(row["vehicle_type"]),
                    "mm": f"{text(row['make'])} {text(row['model'])}",
                    "reg": text(row["registration_number"]),
                    "attrs": json_clob(attrs),
                },
            )
            existing = execute_scalar(
                cursor,
                "SELECT vehicle_id FROM vehicles WHERE external_reference = :x",
                {"x": ext},
            )
        vehicle_map[ext] = int(existing)
        ensure_case_link(cursor, "case_vehicles", "vehicle_id", case_id, int(existing))

        owner = text(row["owner_person_id"])
        if owner in entity_map:
            exists = execute_scalar(
                cursor,
                """
                SELECT COUNT(*) FROM entity_vehicles
                WHERE entity_id = :e AND vehicle_id = :v
                """,
                {"e": entity_map[owner], "v": int(existing)},
            )
            if not exists:
                cursor.execute(
                    """
                    INSERT INTO entity_vehicles (
                        entity_vehicle_id, entity_id, vehicle_id,
                        relationship_type, valid_from
                    )
                    VALUES (
                        SEQ_ENTITY_VEHICLES.NEXTVAL,
                        :e, :v, 'OWNER', :vf
                    )
                    """,
                    {
                        "e": entity_map[owner],
                        "v": int(existing),
                        "vf": parse_time(row["registration_date"]),
                    },
                )


def load_relationships(cursor):
    df = read_csv("01_PEOPLE/relationships/relationships.csv")
    existing_count = int(execute_scalar(cursor, "SELECT COUNT(*) FROM entity_relationships"))
    if existing_count == len(df):
        print(f"  Relationships already present: {existing_count} — skipped")
        return
    if existing_count != 0:
        raise RuntimeError(
            f"ENTITY_RELATIONSHIPS contains {existing_count} rows but source contains {len(df)}. "
            "Refusing to risk duplicate or partial ingestion."
        )

    for _, row in df.iterrows():
        relationship_type = text(row["relationship_type"]).upper()
        if relationship_type not in RELATIONSHIP_TYPES:
            raise RuntimeError(f"Unsupported relationship type: {relationship_type}")
        a = text(row["person_a"])
        b = text(row["person_b"])
        if a not in entity_map or b not in entity_map:
            raise RuntimeError(f"Relationship {text(row['relationship_id'])} references unknown entity")
        attrs = {
            "source_relationship_id": text(row["relationship_id"]),
            "source_relationship_type": relationship_type,
            "documented": text(row["documented"]),
        }
        cursor.execute(
            """
            INSERT INTO entity_relationships (
                relationship_id, relationship_type_id,
                source_entity_id, target_entity_id, attributes
            )
            VALUES (
                SEQ_ENTITY_RELATIONSHIPS.NEXTVAL, :rt, :a, :b, :attrs
            )
            """,
            {
                "rt": RELATIONSHIP_TYPES[relationship_type],
                "a": entity_map[a],
                "b": entity_map[b],
                "attrs": json_clob(attrs),
            },
        )


def insert_event(cursor, event_source, event_type_id, event_time,
                 location_id=None, confidence=None, description=None,
                 attributes=None, end_time=None):
    existing = execute_scalar(
        cursor,
        "SELECT event_id FROM events WHERE source_reference = :s",
        {"s": event_source},
    )
    if existing is not None:
        return int(existing)
    cursor.execute(
        """
        INSERT INTO events (
            event_id, event_type_id, event_time, end_time,
            location_id, source_reference, confidence_score,
            description, attributes
        )
        VALUES (
            SEQ_EVENTS.NEXTVAL, :t, :et, :endt, :loc, :src,
            :conf, :descr, :attrs
        )
        """,
        {
            "t": event_type_id,
            "et": event_time,
            "endt": end_time,
            "loc": location_id,
            "src": event_source[:500],
            "conf": confidence,
            "descr": description,
            "attrs": json_clob(attributes or {}),
        },
    )
    return int(execute_scalar(
        cursor,
        "SELECT event_id FROM events WHERE source_reference = :s",
        {"s": event_source[:500]},
    ))


def link_entity_event(cursor, entity_id, event_id, role):
    exists = execute_scalar(
        cursor,
        """
        SELECT COUNT(*) FROM entity_events
        WHERE entity_id = :e AND event_id = :v AND NVL(role, ' ') = NVL(:r, ' ')
        """,
        {"e": entity_id, "v": event_id, "r": role},
    )
    if not exists:
        cursor.execute(
            """
            INSERT INTO entity_events (
                entity_event_id, entity_id, event_id, role
            )
            VALUES (SEQ_ENTITY_EVENTS.NEXTVAL, :e, :v, :r)
            """,
            {"e": entity_id, "v": event_id, "r": role},
        )


def insert_evidence(cursor, source_reference, evidence_type_id,
                    collected_at=None, confidence=None,
                    description=None, attributes=None):
    existing = execute_scalar(
        cursor,
        "SELECT evidence_id FROM evidence WHERE source_reference = :s",
        {"s": source_reference[:500]},
    )
    if existing is not None:
        return int(existing)
    if confidence is None:
        confidence = execute_scalar(
            cursor,
            "SELECT base_weight FROM evidence_types WHERE evidence_type_id = :i",
            {"i": evidence_type_id},
        )
    confidence = max(0.0, min(1.0, float(confidence)))
    cursor.execute(
        """
        INSERT INTO evidence (
            evidence_id, evidence_type_id, collected_at,
            source_reference, base_confidence, attributes, description
        )
        VALUES (
            SEQ_EVIDENCE.NEXTVAL, :t, :ct, :src, :conf, :attrs, :descr
        )
        """,
        {
            "t": evidence_type_id,
            "ct": collected_at,
            "src": source_reference[:500],
            "conf": confidence,
            "attrs": json_clob(attributes or {}),
            "descr": description,
        },
    )
    return int(execute_scalar(
        cursor,
        "SELECT evidence_id FROM evidence WHERE source_reference = :s",
        {"s": source_reference[:500]},
    ))


def link_evidence_entity(cursor, evidence_id, entity_id, confidence=1.0, role=None):
    exists = execute_scalar(
        cursor,
        """
        SELECT COUNT(*) FROM evidence_entities
        WHERE evidence_id = :e AND entity_id = :n
          AND NVL(relation_role, ' ') = NVL(:r, ' ')
        """,
        {"e": evidence_id, "n": entity_id, "r": role},
    )
    if not exists:
        cursor.execute(
            """
            INSERT INTO evidence_entities (
                evidence_entity_id, evidence_id, entity_id,
                association_confidence, relation_role
            )
            VALUES (
                SEQ_EVIDENCE_ENTITIES.NEXTVAL,
                :e, :n, :c, :r
            )
            """,
            {
                "e": evidence_id,
                "n": entity_id,
                "c": max(0.0, min(1.0, float(confidence))),
                "r": role,
            },
        )


def link_evidence_event(cursor, evidence_id, event_id):
    exists = execute_scalar(
        cursor,
        """
        SELECT COUNT(*) FROM evidence_events
        WHERE evidence_id = :e AND event_id = :v
        """,
        {"e": evidence_id, "v": event_id},
    )
    if not exists:
        cursor.execute(
            """
            INSERT INTO evidence_events (
                evidence_event_id, evidence_id, event_id
            )
            VALUES (SEQ_EVIDENCE_EVENTS.NEXTVAL, :e, :v)
            """,
            {"e": evidence_id, "v": event_id},
        )


def load_communications(cursor, case_id):
    total = 0

    calls = read_csv("03_COMMUNICATIONS/calls/calls.csv")
    for _, row in calls.iterrows():
        a, b = text(row["caller_person_id"]), text(row["receiver_person_id"])
        if a not in entity_map or b not in entity_map:
            raise RuntimeError(f"Call {text(row['record_id'])} references unknown entity")
        start = parse_time(row["timestamp"])
        duration = int(row["duration_seconds"])
        end = start + timedelta(seconds=duration)
        source = f"CALL:{text(row['record_id'])}"
        comm_id = execute_scalar(
            cursor,
            "SELECT communication_id FROM communications WHERE source_reference = :s",
            {"s": source},
        )
        if comm_id is None:
            cursor.execute(
                """
                INSERT INTO communications (
                    communication_id, communication_type_id,
                    sender_entity_id, receiver_entity_id,
                    start_time, end_time, duration_seconds,
                    status, content, source_reference, attributes
                )
                VALUES (
                    SEQ_COMMUNICATIONS.NEXTVAL, 1, :a, :b,
                    :st, :et, :dur, :status, NULL, :src, :attrs
                )
                """,
                {
                    "a": entity_map[a], "b": entity_map[b],
                    "st": start, "et": end, "dur": duration,
                    "status": text(row["call_type"]), "src": source,
                    "attrs": json_clob({
                        "caller_number": text(row["caller_number"]),
                        "receiver_number": text(row["receiver_number"]),
                        "tower_reference": text(row["tower_reference"]),
                        "source_system": text(row["source_system"]),
                    }),
                },
            )
            comm_id = execute_scalar(cursor, "SELECT communication_id FROM communications WHERE source_reference = :s", {"s": source})
        event_id = insert_event(
            cursor, source, EVENT_TYPES["COMMUNICATION"], start,
            description="Telephone call",
            attributes={"record_id": text(row["record_id"]), "source_type": "CALL"},
            end_time=end,
        )
        link_entity_event(cursor, entity_map[a], event_id, "SENDER")
        link_entity_event(cursor, entity_map[b], event_id, "RECEIVER")
        ensure_case_link(cursor, "case_communications", "communication_id", case_id, int(comm_id))
        total += 1

    messages = read_csv("03_COMMUNICATIONS/messages/messages.csv")
    for _, row in messages.iterrows():
        a, b = text(row["sender_person_id"]), text(row["receiver_person_id"])
        if a not in entity_map or b not in entity_map:
            raise RuntimeError(f"Message {text(row['message_id'])} references unknown entity")
        start = parse_time(row["timestamp"])
        source = f"MSG:{text(row['message_id'])}"
        comm_id = execute_scalar(cursor, "SELECT communication_id FROM communications WHERE source_reference = :s", {"s": source})
        if comm_id is None:
            cursor.execute(
                """
                INSERT INTO communications (
                    communication_id, communication_type_id,
                    sender_entity_id, receiver_entity_id, start_time,
                    status, content, source_reference, attributes
                )
                VALUES (
                    SEQ_COMMUNICATIONS.NEXTVAL, 4, :a, :b, :st,
                    :status, :content, :src, :attrs
                )
                """,
                {
                    "a": entity_map[a], "b": entity_map[b], "st": start,
                    "status": "deleted" if bool(row["deleted_flag"]) else "recorded",
                    "content": text(row["body"]), "src": source,
                    "attrs": json_clob({
                        "message_type": text(row["message_type"]),
                        "deleted_flag": bool(row["deleted_flag"]),
                        "edited_flag": bool(row["edited_flag"]),
                        "source_device": text(row["source_device"]),
                    }),
                },
            )
            comm_id = execute_scalar(cursor, "SELECT communication_id FROM communications WHERE source_reference = :s", {"s": source})
        event_id = insert_event(cursor, source, EVENT_TYPES["COMMUNICATION"], start,
                                description="Message communication",
                                attributes={"record_id": text(row["message_id"]), "source_type": "MESSAGE"})
        link_entity_event(cursor, entity_map[a], event_id, "SENDER")
        link_entity_event(cursor, entity_map[b], event_id, "RECEIVER")
        ensure_case_link(cursor, "case_communications", "communication_id", case_id, int(comm_id))
        total += 1

    emails = read_csv("03_COMMUNICATIONS/emails/emails.csv")
    for _, row in emails.iterrows():
        a, b = text(row["sender_person_id"]), text(row["receiver_person_id"])
        if a not in entity_map or b not in entity_map:
            raise RuntimeError(f"Email {text(row['email_id'])} references unknown entity")
        start = parse_time(row["timestamp"])
        source = f"EMAIL:{text(row['email_id'])}"
        comm_id = execute_scalar(cursor, "SELECT communication_id FROM communications WHERE source_reference = :s", {"s": source})
        if comm_id is None:
            cursor.execute(
                """
                INSERT INTO communications (
                    communication_id, communication_type_id,
                    sender_entity_id, receiver_entity_id, start_time,
                    status, content, source_reference, attributes
                )
                VALUES (
                    SEQ_COMMUNICATIONS.NEXTVAL, 3, :a, :b, :st,
                    'recorded', :content, :src, :attrs
                )
                """,
                {
                    "a": entity_map[a], "b": entity_map[b], "st": start,
                    "content": text(row["body"]), "src": source,
                    "attrs": json_clob({
                        "sender_email": text(row["sender_email"]),
                        "receiver_email": text(row["receiver_email"]),
                        "cc": text(row["cc"]),
                        "subject": text(row["subject"]),
                    }),
                },
            )
            comm_id = execute_scalar(cursor, "SELECT communication_id FROM communications WHERE source_reference = :s", {"s": source})
        event_id = insert_event(cursor, source, EVENT_TYPES["COMMUNICATION"], start,
                                description="Email communication",
                                attributes={"record_id": text(row["email_id"]), "source_type": "EMAIL"})
        link_entity_event(cursor, entity_map[a], event_id, "SENDER")
        link_entity_event(cursor, entity_map[b], event_id, "RECEIVER")
        ensure_case_link(cursor, "case_communications", "communication_id", case_id, int(comm_id))
        total += 1

    return total


def load_transactions(cursor, case_id):
    df = read_csv("04_FINANCIAL/transactions/transactions.csv")
    count = 0

    for _, row in df.iterrows():
        person = text(row["person_id"])
        if person not in entity_map:
            raise RuntimeError(f"Transaction {text(row['transaction_id'])} references unknown person {person}")

        counterparty = text(row["counterparty"]) or "Unknown counterparty"
        cp_external = None
        match = re.search(r"\bP\d{3}\b", counterparty)
        if match and match.group(0) in entity_map:
            cp_external = match.group(0)
        else:
            name_match = next((k for k, v in entity_map.items() if k.startswith("P") and False), None)

        if cp_external:
            cp_entity = entity_map[cp_external]
        else:
            cp_key = "ORG:" + re.sub(r"[^A-Za-z0-9]+", "_", counterparty.upper()).strip("_")[:90]
            cp_entity = insert_entity(cursor, cp_key, counterparty, ENTITY_TYPES["ORGANIZATION"])
            entity_map.setdefault(cp_key, cp_entity)

        source = f"TXN:{text(row['transaction_id'])}"
        txn_id = execute_scalar(cursor, "SELECT transaction_id FROM transactions WHERE source_reference = :s", {"s": source})

        debit_credit = text(row["debit_credit"]).lower()
        if debit_credit == "credit":
            sender = cp_entity
            receiver = entity_map[person]
        else:
            sender = entity_map[person]
            receiver = cp_entity

        if txn_id is None:
            cursor.execute(
                """
                INSERT INTO transactions (
                    transaction_id, sender_entity_id, receiver_entity_id,
                    amount, currency, transaction_type, account_reference,
                    transaction_time, status, source_reference, attributes
                )
                VALUES (
                    SEQ_TRANSACTIONS.NEXTVAL, :s, :r, :amt, 'INR',
                    :tt, :acct, :ttime, 'RECORDED', :src, :attrs
                )
                """,
                {
                    "s": sender, "r": receiver,
                    "amt": number(row["amount"]),
                    "tt": debit_credit,
                    "acct": text(row["account_ref"]),
                    "ttime": parse_time(row["timestamp"]),
                    "src": source,
                    "attrs": json_clob({
                        "person_id": person,
                        "counterparty": counterparty,
                        "merchant": text(row["merchant"]),
                        "location_id": text(row["location_id"]),
                        "channel": text(row["channel"]),
                        "reference_number": text(row["reference_number"]),
                        "description": text(row["description"]),
                        "source_system": text(row["source_system"]),
                    }),
                },
            )
            txn_id = execute_scalar(cursor, "SELECT transaction_id FROM transactions WHERE source_reference = :s", {"s": source})

        event_id = insert_event(
            cursor, source, EVENT_TYPES["TRANSACTION"], parse_time(row["timestamp"]),
            location_map.get(text(row["location_id"])),
            description="Financial transaction",
            attributes={"transaction_id": text(row["transaction_id"]), "person_id": person},
        )
        link_entity_event(cursor, sender, event_id, "SENDER")
        link_entity_event(cursor, receiver, event_id, "RECEIVER")

        evidence_id = insert_evidence(
            cursor, source, EVIDENCE_TYPES["FINANCIAL"],
            collected_at=parse_time(row["timestamp"]),
            description=text(row["description"]),
            attributes={"transaction_id": text(row["transaction_id"]), "counterparty": counterparty},
        )
        link_evidence_entity(cursor, evidence_id, entity_map[person], role="ACCOUNT_HOLDER")
        ensure_case_link(cursor, "case_transactions", "transaction_id", case_id, int(txn_id))
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        link_evidence_event(cursor, evidence_id, event_id)
        count += 1

    return count


def load_vehicle_sightings(cursor, case_id):
    df = read_csv("05_VEHICLES/sightings/vehicle_sightings.csv")
    count = 0
    for _, row in df.iterrows():
        vid = text(row["vehicle_id"])
        lid = text(row["location_id"])
        if vid not in vehicle_map or lid not in location_map:
            raise RuntimeError(f"Vehicle sighting {text(row['sighting_id'])} has an unknown vehicle/location")
        source = f"VEHICLE_SIGHTING:{text(row['sighting_id'])}"
        sighting_id = execute_scalar(cursor, "SELECT sighting_id FROM vehicle_sightings WHERE source_reference = :s", {"s": source})
        if sighting_id is None:
            cursor.execute(
                """
                INSERT INTO vehicle_sightings (
                    sighting_id, vehicle_id, location_id, observed_at,
                    confidence_score, source_reference, attributes
                )
                VALUES (
                    SEQ_VEHICLE_SIGHTINGS.NEXTVAL, :v, :l, :t,
                    :c, :s, :a
                )
                """,
                {
                    "v": vehicle_map[vid], "l": location_map[lid],
                    "t": parse_time(row["timestamp"]), "c": number(row["confidence"]),
                    "s": source,
                    "a": json_clob({"registration_as_captured": text(row["registration_as_captured"]), "source": text(row["source"])}),
                },
            )
            sighting_id = execute_scalar(cursor, "SELECT sighting_id FROM vehicle_sightings WHERE source_reference = :s", {"s": source})
        event_id = insert_event(cursor, source, EVENT_TYPES["MOVEMENT"], parse_time(row["timestamp"]), location_map[lid], number(row["confidence"]), "Vehicle sighting", {"vehicle_id": vid})
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["CCTV"], parse_time(row["timestamp"]), number(row["confidence"]), "Vehicle sighting", {"vehicle_id": vid, "location_id": lid, "source": text(row["source"])})
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_vehicles", "vehicle_id", case_id, vehicle_map[vid])
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        count += 1
    return count


def load_gps(cursor, case_id):
    # gps_logs_full.csv is the complete movement dataset. gps_logs.csv is a subset.
    df = read_csv("06_DEVICES/gps/gps_logs_full.csv")
    count = 0
    for _, row in df.iterrows():
        pid, lid = text(row["person_id"]), text(row["location_id"])
        if pid not in entity_map or lid not in location_map:
            raise RuntimeError(f"GPS {text(row['movement_id'])} references unknown entity/location")
        source = f"GPS:{text(row['movement_id'])}"
        event_id = insert_event(cursor, source, EVENT_TYPES["MOVEMENT"], parse_time(row["timestamp"]), location_map[lid], number(row["confidence"]), "GPS movement observation", {"movement_id": text(row["movement_id"]), "accuracy_meters": number(row["accuracy_meters"]), "source": text(row["source"])})
        link_entity_event(cursor, entity_map[pid], event_id, "OBSERVED_SUBJECT")
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["GPS"], parse_time(row["timestamp"]), number(row["confidence"]), "GPS movement observation", {"movement_id": text(row["movement_id"]), "accuracy_meters": number(row["accuracy_meters"]), "source": text(row["source"])})
        link_evidence_entity(cursor, evidence_id, entity_map[pid], number(row["confidence"]), "SUBJECT")
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        count += 1
    return count


def load_access_and_visitors(cursor, case_id):
    count = 0
    df = read_csv("07_ACCESS_SECURITY/access_logs/access_logs.csv")
    for _, row in df.iterrows():
        pid, lid = text(row["person_id"]), text(row["location_id"])
        if pid not in entity_map or lid not in location_map:
            raise RuntimeError(f"Access {text(row['access_id'])} references unknown entity/location")
        source = f"ACCESS:{text(row['access_id'])}"
        event_id = insert_event(cursor, source, EVENT_TYPES["ACCESS"], parse_time(row["timestamp"]), location_map[lid], None, "Access-control event", {"access_id": text(row["access_id"]), "access_result": text(row["access_result"]), "door": text(row["door"]), "reader_id": text(row["reader_id"])})
        link_entity_event(cursor, entity_map[pid], event_id, "SUBJECT")
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["ACCESS_LOG"], parse_time(row["timestamp"]), None, "Access-control record", {"access_result": text(row["access_result"]), "door": text(row["door"]), "reader_id": text(row["reader_id"])})
        link_evidence_entity(cursor, evidence_id, entity_map[pid], role="SUBJECT")
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        count += 1

    df = read_csv("07_ACCESS_SECURITY/visitor_logs/visitor_logs.csv")
    for _, row in df.iterrows():
        lid, host = text(row["location_id"]), text(row["host_person_id"])
        if lid not in location_map or host not in entity_map:
            raise RuntimeError(f"Visitor {text(row['visitor_log_id'])} references unknown location/host")
        source = f"VISITOR:{text(row['visitor_log_id'])}"
        event_id = insert_event(cursor, source, EVENT_TYPES["ACCESS"], parse_time(row["timestamp"]), location_map[lid], None, "Visitor log", {"visitor_name": text(row["visitor_name"]), "purpose": text(row["purpose"]), "host_person_id": host})
        link_entity_event(cursor, entity_map[host], event_id, "HOST")
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["ACCESS_LOG"], parse_time(row["timestamp"]), None, "Visitor log", {"visitor_name": text(row["visitor_name"]), "purpose": text(row["purpose"])})
        link_evidence_entity(cursor, evidence_id, entity_map[host], role="HOST")
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        count += 1
    return count


def load_cctv(cursor, case_id):
    cams = read_csv("08_CCTV/metadata/cameras.csv")
    annotations = read_csv("08_CCTV/annotations/cctv_annotations.csv")
    camera_locations = {text(r["camera_id"]): text(r["location_id"]) for _, r in cams.iterrows()}
    count = 0
    for _, row in annotations.iterrows():
        cam = text(row["camera_id"])
        lid = camera_locations.get(cam)
        if lid not in location_map:
            raise RuntimeError(f"CCTV annotation {text(row['annotation_id'])} references unknown camera/location")
        source = f"CCTV:{text(row['annotation_id'])}"
        event_id = insert_event(cursor, source, EVENT_TYPES["LOCATION_OBSERVATION"], parse_time(row["timestamp"]), location_map[lid], number(row["confidence"]), text(row["description"]), {"annotation_id": text(row["annotation_id"]), "camera_id": cam})
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["CCTV"], parse_time(row["timestamp"]), number(row["confidence"]), text(row["description"]), {"camera_id": cam, "location_id": lid})
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        count += 1
    return count


def load_audio(cursor, case_id):
    meta = read_csv("09_AUDIO/recordings/audio_metadata.csv")
    count = 0
    for _, row in meta.iterrows():
        aid = text(row["audio_id"])
        transcript_path = ROOT / "09_AUDIO" / "transcripts" / f"{aid}_transcript.txt"
        transcript = transcript_path.read_text(encoding="utf-8", errors="ignore") if transcript_path.exists() else None
        speaker = text(row["speaker_person_id"])
        source = f"AUDIO:{aid}"
        event_id = insert_event(cursor, source, EVENT_TYPES["COMMUNICATION"], parse_time(row["timestamp"]), None, number(row["transcript_confidence"]), "Audio recording", {"audio_id": aid, "source": text(row["source"]), "language": text(row["language"])})
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["DIGITAL"], parse_time(row["timestamp"]), number(row["transcript_confidence"]), transcript or "Audio recording", {"audio_id": aid, "source": text(row["source"]), "language": text(row["language"]), "speaker_confidence": text(row["speaker_confidence"])})
        if speaker in entity_map:
            link_entity_event(cursor, entity_map[speaker], event_id, "SPEAKER")
            link_evidence_entity(cursor, evidence_id, entity_map[speaker], role="SPEAKER")
        link_evidence_event(cursor, evidence_id, event_id)
        ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        count += 1
    return count


def forensic_confidence(value):
    v = text(value)
    if v is None:
        return None
    return {"very high": 0.95, "high": 0.85, "medium": 0.70, "low": 0.50}.get(v.lower(), 0.60)


def load_forensics(cursor, case_id):
    df = read_csv("10_FORENSICS/reports/forensic_reports.csv")
    count = 0
    for _, row in df.iterrows():
        et = text(row["evidence_type"]).lower()
        if "fingerprint" in et:
            etid = EVIDENCE_TYPES["FINGERPRINT"]
        elif "dna" in et:
            etid = EVIDENCE_TYPES["DNA"]
        elif "digital" in et:
            etid = EVIDENCE_TYPES["DIGITAL"]
        else:
            etid = EVIDENCE_TYPES["DOCUMENT"]
        source = f"FORENSIC:{text(row['evidence_id'])}"
        evidence_id = insert_evidence(cursor, source, etid, parse_time(row["collection_time"]), forensic_confidence(row["confidence"]), text(row["finding"]), {"analyst": text(row["analyst"]), "method": text(row["method"]), "limitations": text(row["limitations"]), "report_timestamp": text(row["report_timestamp"]), "location_id": text(row["location_id"])})
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        if text(row["location_id"]) in location_map:
            event_id = insert_event(cursor, source, EVENT_TYPES["OTHER"], parse_time(row["collection_time"]), location_map[text(row["location_id"])], forensic_confidence(row["confidence"]), text(row["finding"]), {"evidence_id": text(row["evidence_id"]), "source_type": "FORENSIC"})
            link_evidence_event(cursor, evidence_id, event_id)
            ensure_case_link(cursor, "case_events", "event_id", case_id, event_id)
        count += 1
    return count


def load_witnesses(cursor, case_id):
    count = 0
    folder = ROOT / "01_PEOPLE" / "interviews"
    for path in sorted(folder.glob("WIT*.txt")):
        raw = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Witness:\s*(P\d{3})", raw)
        pid = m.group(1) if m else None
        date_match = re.search(r"Interview Date:\s*(\d{4}-\d{2}-\d{2})", raw)
        collected = parse_time((date_match.group(1) + " 00:00:00") if date_match else "2026-03-23 00:00:00")
        source = f"WITNESS:{path.stem}"
        evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["WITNESS"], collected, 0.55, raw[:3900], {"witness_file": path.name, "witness_person_id": pid})
        ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
        if pid in entity_map:
            link_evidence_entity(cursor, evidence_id, entity_map[pid], role="WITNESS")
        count += 1
    return count


def load_documents(cursor, case_id):
    specs = [
        ("11_LEGAL_BUSINESS/employment", "DOCUMENT"),
        ("11_LEGAL_BUSINESS/invoices", "DOCUMENT"),
        ("11_LEGAL_BUSINESS/leases", "DOCUMENT"),
        ("12_PUBLIC_INFORMATION/news", "DOCUMENT"),
        ("12_PUBLIC_INFORMATION/public_posts", "DOCUMENT"),
    ]
    count = 0
    for folder, typ in specs:
        base = ROOT / folder
        for path in sorted(base.iterdir()):
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8", errors="ignore")
            source = f"DOCUMENT:{folder}/{path.name}"
            evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES[typ], None, 0.60, raw[:3900], {"file_name": path.name, "category": folder})
            ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
            count += 1
    return count


def load_public_and_investigation_material(cursor, case_id):
    # Contradictions are operational analytical material, so preserve them
    # as DOCUMENT evidence without importing evaluation-only ground truth.
    count = 0
    contradiction_file = ROOT / "13_INVESTIGATION_MATERIAL" / "contradiction_register" / "contradictions.csv"
    if contradiction_file.exists():
        df = pd.read_csv(contradiction_file)
        for _, row in df.iterrows():
            cid = text(row.iloc[0])
            source = f"CONTRADICTION:{cid}"
            attrs = {str(k): text(row[k]) for k in df.columns}
            evidence_id = insert_evidence(cursor, source, EVIDENCE_TYPES["DOCUMENT"], None, 0.60, json_clob(attrs), {"category": "contradiction_register", "contradiction_id": cid})
            ensure_case_link(cursor, "case_evidence", "evidence_id", case_id, evidence_id)
            count += 1
    return count


def validate(cursor, case_id):
    expected = {
        "case": 1,
        "locations": len(pd.read_csv(ROOT / "02_LOCATIONS/locations.csv")),
        "people": len(pd.read_csv(ROOT / "01_PEOPLE/person_profiles/people.csv")),
        "vehicles": len(pd.read_csv(ROOT / "05_VEHICLES/registry/vehicles.csv")),
        "relationships": len(pd.read_csv(ROOT / "01_PEOPLE/relationships/relationships.csv")),
        "calls": len(pd.read_csv(ROOT / "03_COMMUNICATIONS/calls/calls.csv")),
        "messages": len(pd.read_csv(ROOT / "03_COMMUNICATIONS/messages/messages.csv")),
        "emails": len(pd.read_csv(ROOT / "03_COMMUNICATIONS/emails/emails.csv")),
        "transactions": len(pd.read_csv(ROOT / "04_FINANCIAL/transactions/transactions.csv")),
        "vehicle_sightings": len(pd.read_csv(ROOT / "05_VEHICLES/sightings/vehicle_sightings.csv")),
        "gps": len(pd.read_csv(ROOT / "06_DEVICES/gps/gps_logs_full.csv")),
        "access": len(pd.read_csv(ROOT / "07_ACCESS_SECURITY/access_logs/access_logs.csv")),
        "visitors": len(pd.read_csv(ROOT / "07_ACCESS_SECURITY/visitor_logs/visitor_logs.csv")),
        "cctv": len(pd.read_csv(ROOT / "08_CCTV/annotations/cctv_annotations.csv")),
        "audio": len(pd.read_csv(ROOT / "09_AUDIO/recordings/audio_metadata.csv")),
        "forensics": len(pd.read_csv(ROOT / "10_FORENSICS/reports/forensic_reports.csv")),
        "witnesses": len(list((ROOT / "01_PEOPLE/interviews").glob("WIT*.txt"))),
    }

    actual = {
        "case": execute_scalar(cursor, "SELECT COUNT(*) FROM investigation_cases WHERE case_id = :c", {"c": case_id}),
        "locations": execute_scalar(cursor, "SELECT COUNT(*) FROM case_locations WHERE case_id = :c", {"c": case_id}),
        "people": execute_scalar(cursor, "SELECT COUNT(*) FROM case_entities WHERE case_id = :c", {"c": case_id}),
        "vehicles": execute_scalar(cursor, "SELECT COUNT(*) FROM case_vehicles WHERE case_id = :c", {"c": case_id}),
        "relationships": execute_scalar(cursor, "SELECT COUNT(*) FROM entity_relationships"),
        "communications": execute_scalar(cursor, "SELECT COUNT(*) FROM case_communications WHERE case_id = :c", {"c": case_id}),
        "transactions": execute_scalar(cursor, "SELECT COUNT(*) FROM case_transactions WHERE case_id = :c", {"c": case_id}),
        "vehicle_sightings": execute_scalar(cursor, "SELECT COUNT(*) FROM vehicle_sightings vs JOIN case_vehicles cv ON cv.vehicle_id = vs.vehicle_id WHERE cv.case_id = :c", {"c": case_id}),
        "events": execute_scalar(cursor, "SELECT COUNT(*) FROM case_events WHERE case_id = :c", {"c": case_id}),
        "evidence": execute_scalar(cursor, "SELECT COUNT(*) FROM case_evidence WHERE case_id = :c", {"c": case_id}),
    }

    if actual["case"] != 1:
        raise RuntimeError("Case validation failed")
    if actual["locations"] != expected["locations"]:
        raise RuntimeError(f"Location validation failed: expected {expected['locations']}, got {actual['locations']}")
    if actual["people"] < expected["people"]:
        raise RuntimeError(f"Entity validation failed: expected at least {expected['people']}, got {actual['people']}")
    if actual["vehicles"] != expected["vehicles"]:
        raise RuntimeError(f"Vehicle validation failed: expected {expected['vehicles']}, got {actual['vehicles']}")
    if actual["relationships"] != expected["relationships"]:
        raise RuntimeError(f"Relationship validation failed: expected {expected['relationships']}, got {actual['relationships']}")
    if actual["communications"] != expected["calls"] + expected["messages"] + expected["emails"]:
        raise RuntimeError("Communication validation failed")
    if actual["transactions"] != expected["transactions"]:
        raise RuntimeError("Transaction validation failed")
    if actual["vehicle_sightings"] != expected["vehicle_sightings"]:
        raise RuntimeError("Vehicle-sighting validation failed")

    return actual


def main():
    cursor = connection.cursor()
    try:
        print()
        print("=" * 70)
        print("CRIMEMIND FULL WORLD INGESTION")
        print("=" * 70)
        print("Connected to Oracle:", connection.version)
        print()

        if not ROOT.exists():
            raise FileNotFoundError(f"Synthetic world not found: {ROOT}")
        if (ROOT / "14_EVALUATION_ONLY" / "ground_truth.json").exists():
            print("✓ Evaluation-only ground truth detected and excluded")

        case_id = load_case(cursor)
        print(f"✓ Case: CASE_ID={case_id}")

        load_locations(cursor, case_id)
        print(f"✓ Locations: {len(location_map)}")

        load_people(cursor, case_id)
        print(f"✓ People/entities mapped: {len(entity_map)}")

        load_vehicles(cursor, case_id)
        print(f"✓ Vehicles: {len(vehicle_map)}")

        load_relationships(cursor)
        print("✓ Relationships")

        comm_count = load_communications(cursor, case_id)
        print(f"✓ Communications: {comm_count}")

        txn_count = load_transactions(cursor, case_id)
        print(f"✓ Transactions: {txn_count}")

        vs_count = load_vehicle_sightings(cursor, case_id)
        print(f"✓ Vehicle sightings: {vs_count}")

        gps_count = load_gps(cursor, case_id)
        print(f"✓ GPS/movement: {gps_count}")

        access_count = load_access_and_visitors(cursor, case_id)
        print(f"✓ Access + visitors: {access_count}")

        cctv_count = load_cctv(cursor, case_id)
        print(f"✓ CCTV annotations: {cctv_count}")

        audio_count = load_audio(cursor, case_id)
        print(f"✓ Audio: {audio_count}")

        forensic_count = load_forensics(cursor, case_id)
        print(f"✓ Forensics: {forensic_count}")

        witness_count = load_witnesses(cursor, case_id)
        print(f"✓ Witness interviews: {witness_count}")

        document_count = load_documents(cursor, case_id)
        print(f"✓ Legal/business/public documents: {document_count}")

        contradiction_count = load_public_and_investigation_material(cursor, case_id)
        print(f"✓ Contradiction register: {contradiction_count}")

        print()
        print("Running final database validation...")
        actual = validate(cursor, case_id)

        connection.commit()

        print()
        print("=" * 70)
        print("FULL INGESTION SUCCESSFUL")
        print("=" * 70)
        print("✓ Oracle transaction committed")
        print(f"✓ CASE_ID: {case_id}")
        print(f"✓ Locations: {actual['locations']}")
        print(f"✓ People/entities: {actual['people']}")
        print(f"✓ Vehicles: {actual['vehicles']}")
        print(f"✓ Relationships: {actual['relationships']}")
        print(f"✓ Communications: {actual['communications']}")
        print(f"✓ Transactions: {actual['transactions']}")
        print(f"✓ Vehicle sightings: {actual['vehicle_sightings']}")
        print(f"✓ Events: {actual['events']}")
        print(f"✓ Evidence: {actual['evidence']}")
        print("✓ Evaluation-only ground truth was not ingested")
        print()

    except Exception as exc:
        connection.rollback()
        print()
        print("=" * 70)
        print("FULL INGESTION FAILED - ROLLBACK PERFORMED")
        print("=" * 70)
        print(type(exc).__name__, ":", exc)
        raise
    finally:
        cursor.close()
        connection.close()
        print("Oracle connection closed.")


if __name__ == "__main__":
    main()
