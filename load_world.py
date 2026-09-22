from pathlib import Path
import json

import pandas as pd
import oracledb


# ============================================================
# CRIMEMIND - STAGE 2 INGESTION
# ============================================================
#
# Loads relationship data from:
#
#   01_PEOPLE/relationships/relationships.csv
#
# into:
#
#   ENTITY_RELATIONSHIPS
#
# Stage 1 has already loaded:
#   - Investigation case
#   - Locations
#   - People / entities
#   - Vehicles
#
# IMPORTANT:
#   This script commits ONLY if the complete relationship
#   file is processed successfully.
#
#   If ANY error occurs:
#       connection.rollback()
#
#   Therefore, a failed execution does not leave partial
#   relationship data in Oracle.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(
    r".\data\raw\CrimeMind_Synthetic_World_v2"
)

ORACLE_USER = "CRIMEMIND"

ORACLE_PASSWORD = "CrimeMind123"

ORACLE_DSN = "localhost:1521/XE"

ORACLE_CLIENT = (
    r"C:\oraclexe\app\oracle\product\11.2.0"
    r"\server\bin"
)


# ============================================================
# ORACLE CLIENT INITIALIZATION
# ============================================================

oracledb.init_oracle_client(
    lib_dir=ORACLE_CLIENT
)


# ============================================================
# ORACLE CONNECTION
# ============================================================

connection = oracledb.connect(
    user=ORACLE_USER,
    password=ORACLE_PASSWORD,
    dsn=ORACLE_DSN
)

print(
    f"Connected to Oracle: {connection.version}"
)


# ============================================================
# EXTERNAL ID → ORACLE ID MAPS
# ============================================================

person_map = {}

location_map = {}

vehicle_map = {}


# ============================================================
# ENTITY TYPE MAPPING
# ============================================================

ENTITY_TYPES = {

    "PERSON": 1,

    "ORGANIZATION": 2,

    "ACCOUNT": 3,

    "DEVICE": 4,

    "UNKNOWN": 5,
}


# ============================================================
# RELATIONSHIP TYPE MAPPING
# ============================================================
#
# Oracle reference data:
#
#   1 = ASSOCIATE
#   2 = FAMILY
#   3 = BUSINESS
#   4 = EMPLOYMENT
#   5 = TENANCY
#   6 = CONTACT
#
# The synthetic world contains more specific relationship
# names. Those source names are normalized to the available
# Oracle relationship categories.
#
# The ORIGINAL source relationship type is preserved in the
# ATTRIBUTES JSON column, so normalization does not erase
# the original source meaning.
# ============================================================

RELATIONSHIP_TYPES = {

    # --------------------------------------------------------
    # Native Oracle relationship types
    # --------------------------------------------------------

    "ASSOCIATE": 1,

    "FAMILY": 2,

    "BUSINESS": 3,

    "EMPLOYMENT": 4,

    "TENANCY": 5,

    "CONTACT": 6,


    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    "EMPLOYER_EMPLOYEE": 4,


    # --------------------------------------------------------
    # Tenancy
    # --------------------------------------------------------

    "LANDLORD_TENANT": 5,


    # --------------------------------------------------------
    # Personal / social relationships
    # --------------------------------------------------------

    "FRIEND": 1,

    "FORMER_PARTNER": 1,

    "NEIGHBOR": 1,

    "PROFESSOR_STUDENT": 1,

    "FORMER_COWORKER": 1,


    # --------------------------------------------------------
    # Professional / business relationships
    # --------------------------------------------------------

    "LAWYER_CLIENT": 3,

    "COMPETITOR": 3,

    "SERVICE_RELATIONSHIP": 3,

    "DEBT": 3,

    "DOCTOR_PATIENT": 3,

    "BUSINESS_PARTNER": 3,
}


# ============================================================
# HELPER: READ CSV
# ============================================================

def read_csv(relative_path):

    path = ROOT / relative_path

    if not path.exists():

        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# HELPER: CONVERT DATA TO JSON
# ============================================================

def json_clob(data):

    return json.dumps(
        data,
        ensure_ascii=False
    )


# ============================================================
# LOAD RELATIONSHIPS
# ============================================================

def load_relationships(cursor):

    print()
    print("Loading relationships...")
    print()

    # --------------------------------------------------------
    # Read relationship CSV
    # --------------------------------------------------------

    df = read_csv(
        "01_PEOPLE/relationships/relationships.csv"
    )


    # --------------------------------------------------------
    # Validate expected columns
    # --------------------------------------------------------

    required_columns = {
        "relationship_id",
        "person_a",
        "person_b",
        "relationship_type",
        "documented",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise RuntimeError(
            "relationships.csv is missing "
            f"required columns: "
            f"{sorted(missing_columns)}"
        )


    # --------------------------------------------------------
    # Track counts
    # --------------------------------------------------------

    loaded = 0

    relationship_type_counts = {}


    # ========================================================
    # PROCESS EVERY RELATIONSHIP
    # ========================================================

    for _, row in df.iterrows():

        # ----------------------------------------------------
        # Source relationship ID
        # ----------------------------------------------------

        relationship_id = str(
            row["relationship_id"]
        ).strip()


        # ----------------------------------------------------
        # Source person A
        # ----------------------------------------------------

        person_a = str(
            row["person_a"]
        ).strip()


        # ----------------------------------------------------
        # Source person B
        # ----------------------------------------------------

        person_b = str(
            row["person_b"]
        ).strip()


        # ----------------------------------------------------
        # Source relationship type
        # ----------------------------------------------------

        relationship_type = str(
            row["relationship_type"]
        ).strip().upper()


        # ----------------------------------------------------
        # Documented flag
        # ----------------------------------------------------

        documented = str(
            row["documented"]
        ).strip().lower()


        # ====================================================
        # VALIDATE PERSON A
        # ====================================================

        if person_a not in person_map:

            raise RuntimeError(
                f"Relationship {relationship_id} "
                f"references unknown person "
                f"{person_a}"
            )


        # ====================================================
        # VALIDATE PERSON B
        # ====================================================

        if person_b not in person_map:

            raise RuntimeError(
                f"Relationship {relationship_id} "
                f"references unknown person "
                f"{person_b}"
            )


        # ====================================================
        # VALIDATE RELATIONSHIP TYPE
        # ====================================================

        if relationship_type not in RELATIONSHIP_TYPES:

            raise RuntimeError(
                f"Relationship {relationship_id} "
                f"has unknown relationship type "
                f"{relationship_type}"
            )


        # ====================================================
        # COUNT SOURCE TYPE
        # ====================================================

        relationship_type_counts[
            relationship_type
        ] = (
            relationship_type_counts.get(
                relationship_type,
                0
            ) + 1
        )


        # ====================================================
        # PRESERVE SOURCE INFORMATION
        # ====================================================
        #
        # This is important.
        #
        # Example:
        #
        #   LAWYER_CLIENT
        #
        # is normalized to Oracle:
        #
        #   BUSINESS
        #
        # but the original source type is retained here.
        # ====================================================

        attributes = {

            "source_relationship_id":
                relationship_id,

            "source_relationship_type":
                relationship_type,

            "documented":
                documented
        }


        # ====================================================
        # INSERT INTO ENTITY_RELATIONSHIPS
        # ====================================================

        cursor.execute(
            """
            INSERT INTO entity_relationships
            (
                relationship_id,
                relationship_type_id,
                source_entity_id,
                target_entity_id,
                attributes
            )
            VALUES
            (
                SEQ_ENTITY_RELATIONSHIPS.NEXTVAL,
                :relationship_type_id,
                :source_entity_id,
                :target_entity_id,
                :attributes
            )
            """,
            {

                "relationship_type_id":
                    RELATIONSHIP_TYPES[
                        relationship_type
                    ],

                "source_entity_id":
                    person_map[person_a],

                "target_entity_id":
                    person_map[person_b],

                "attributes":
                    json_clob(attributes)
            }
        )


        loaded += 1


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print(
        f"✓ Relationships loaded: {loaded}"
    )

    print()
    print("✓ Source relationship types processed:")

    for relationship_type in sorted(
        relationship_type_counts
    ):

        count = relationship_type_counts[
            relationship_type
        ]

        oracle_type_id = RELATIONSHIP_TYPES[
            relationship_type
        ]

        print(
            f"  {relationship_type:<25} "
            f"{count:>3} "
            f"→ Oracle type ID {oracle_type_id}"
        )


# ============================================================
# MAIN INGESTION
# ============================================================

cursor = None


try:

    # ========================================================
    # HEADER
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "CRIMEMIND STAGE 2 INGESTION"
    )

    print(
        "=" * 60
    )

    print()


    # ========================================================
    # CREATE CURSOR
    # ========================================================

    cursor = connection.cursor()


    # ========================================================
    # FIND EXISTING CASE
    # ========================================================

    cursor.execute(
        """
        SELECT case_id
        FROM investigation_cases
        WHERE case_reference =
              'CM-2026-0314-NDP'
        """
    )

    result = cursor.fetchone()


    if result is None:

        raise RuntimeError(
            "CrimeMind case "
            "CM-2026-0314-NDP "
            "was not found in Oracle."
        )


    case_id = int(
        result[0]
    )


    # ========================================================
    # REBUILD ENTITY MAP
    # ========================================================

    cursor.execute(
        """
        SELECT
            entity_id,
            external_reference
        FROM entities
        WHERE external_reference IS NOT NULL
        """
    )


    for entity_id, external_reference in cursor:

        person_map[
            str(external_reference)
        ] = int(entity_id)


    # ========================================================
    # REBUILD LOCATION MAP
    # ========================================================

    cursor.execute(
        """
        SELECT
            location_id,
            external_reference
        FROM locations
        WHERE external_reference IS NOT NULL
        """
    )


    for location_id, external_reference in cursor:

        location_map[
            str(external_reference)
        ] = int(location_id)


    # ========================================================
    # REBUILD VEHICLE MAP
    # ========================================================

    cursor.execute(
        """
        SELECT
            vehicle_id,
            external_reference
        FROM vehicles
        WHERE external_reference IS NOT NULL
        """
    )


    for vehicle_id, external_reference in cursor:

        vehicle_map[
            str(external_reference)
        ] = int(vehicle_id)


    # ========================================================
    # DISPLAY EXISTING DATA
    # ========================================================

    print(
        f"✓ Existing case found: "
        f"CASE_ID={case_id}"
    )

    print(
        f"✓ Entity map rebuilt: "
        f"{len(person_map)}"
    )

    print(
        f"✓ Location map rebuilt: "
        f"{len(location_map)}"
    )

    print(
        f"✓ Vehicle map rebuilt: "
        f"{len(vehicle_map)}"
    )


    # ========================================================
    # LOAD RELATIONSHIPS
    # ========================================================

    load_relationships(
        cursor
    )


    # ========================================================
    # COMMIT
    # ========================================================
    #
    # IMPORTANT:
    #
    # Nothing from this Stage 2 execution is permanently
    # committed until this point.
    # ========================================================

    connection.commit()


    # ========================================================
    # SUCCESS
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "STAGE 2 SUCCESSFUL"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "✓ Relationship ingestion "
        "committed successfully."
    )

    print(
        f"✓ CASE_ID = {case_id}"
    )

    print(
        f"✓ Entities available = "
        f"{len(person_map)}"
    )

    print(
        f"✓ Locations available = "
        f"{len(location_map)}"
    )

    print(
        f"✓ Vehicles available = "
        f"{len(vehicle_map)}"
    )


except Exception as e:

    # ========================================================
    # ROLLBACK
    # ========================================================
    #
    # Any error causes the complete Stage 2 transaction
    # to be rolled back.
    # ========================================================

    connection.rollback()


    print()

    print(
        "=" * 60
    )

    print(
        "STAGE 2 FAILED — "
        "ROLLBACK PERFORMED"
    )

    print(
        "=" * 60
    )

    print(
        type(e).__name__,
        ":",
        e
    )


    raise


finally:

    # ========================================================
    # CLOSE CURSOR
    # ========================================================

    if cursor is not None:

        cursor.close()


    # ========================================================
    # CLOSE CONNECTION
    # ========================================================

    connection.close()


    print()

    print(
        "Oracle connection closed."
    )