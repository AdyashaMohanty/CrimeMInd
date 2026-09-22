from app.db.sql import fetch_all, fetch_one


def dashboard(conn, case_id: int):
    case = fetch_one(conn, """
        SELECT c.case_id,c.case_reference,c.title,c.status,c.opened_at,c.incident_time,
               l.location_name AS incident_location
        FROM investigation_cases c
        LEFT JOIN locations l ON l.location_id=c.incident_location_id
        WHERE c.case_id=%(case_id)s
    """, {"case_id": case_id})

    entities = fetch_all(conn, """
        SELECT e.external_reference AS id,e.display_name AS name,et.type_name AS role,
               'ACTIVE' AS status,1.0::numeric AS score
        FROM case_entities ce
        JOIN entities e ON e.entity_id=ce.entity_id
        JOIN entity_types et ON et.entity_type_id=e.entity_type_id
        WHERE ce.case_id=%(case_id)s
        ORDER BY e.external_reference NULLS LAST,e.entity_id
    """, {"case_id": case_id})

    evidence = fetch_all(conn, """
        SELECT e.evidence_id AS id,et.type_name AS type,
               COALESCE(NULLIF(e.description,''),et.type_name || ' evidence') AS title,
               e.description,e.collected_at AS time,e.source_reference AS source,
               ROUND(e.base_confidence * et.base_weight,4) AS weight,
               'FACT' AS kind
        FROM case_evidence ce
        JOIN evidence e ON e.evidence_id=ce.evidence_id
        JOIN evidence_types et ON et.evidence_type_id=e.evidence_type_id
        WHERE ce.case_id=%(case_id)s
        ORDER BY e.collected_at DESC NULLS LAST,e.evidence_id DESC
        LIMIT 200
    """, {"case_id": case_id})

    communications = fetch_all(conn, """
        SELECT c.communication_id AS id,ct.type_name AS type,c.start_time AS time,
               se.external_reference AS sender,re.external_reference AS receiver,
               c.status,c.duration_seconds,c.content,c.source_reference AS source
        FROM case_communications cc
        JOIN communications c ON c.communication_id=cc.communication_id
        JOIN communication_types ct ON ct.communication_type_id=c.communication_type_id
        JOIN entities se ON se.entity_id=c.sender_entity_id
        JOIN entities re ON re.entity_id=c.receiver_entity_id
        WHERE cc.case_id=%(case_id)s
        ORDER BY c.start_time DESC
        LIMIT 200
    """, {"case_id": case_id})

    transactions = fetch_all(conn, """
        SELECT t.transaction_id AS id,se.external_reference AS sender,re.external_reference AS receiver,
               t.amount,t.currency,t.transaction_type AS type,t.transaction_time,t.status,
               t.source_reference AS source
        FROM case_transactions ct
        JOIN transactions t ON t.transaction_id=ct.transaction_id
        JOIN entities se ON se.entity_id=t.sender_entity_id
        JOIN entities re ON re.entity_id=t.receiver_entity_id
        WHERE ct.case_id=%(case_id)s
        ORDER BY t.transaction_time DESC
        LIMIT 200
    """, {"case_id": case_id})

    locations = fetch_all(conn, """
        SELECT l.location_id AS id,l.location_name AS name,l.location_type AS type,l.address,
               ST_Y(l.geom::geometry) AS latitude,ST_X(l.geom::geometry) AS longitude,
               ARRAY(SELECT e.external_reference FROM case_entities ce2
                     JOIN entity_events ee ON ee.entity_id=ce2.entity_id
                     JOIN events ev ON ev.event_id=ee.event_id
                     JOIN entities e ON e.entity_id=ce2.entity_id
                     WHERE ce2.case_id=%(case_id)s AND ev.location_id=l.location_id
                     GROUP BY e.external_reference) AS entities
        FROM case_locations cl
        JOIN locations l ON l.location_id=cl.location_id
        LEFT JOIN entities e ON FALSE
        WHERE cl.case_id=%(case_id)s
        ORDER BY l.location_id
    """, {"case_id": case_id})

    # Correct the correlated location query separately because the ARRAY above
    # intentionally avoids leaking entities outside the case scope.
    for loc in locations:
        loc["coordinates"] = (
            f"{loc.get('latitude')}, {loc.get('longitude')}"
            if loc.get("latitude") is not None and loc.get("longitude") is not None else "—"
        )

    vehicles = fetch_all(conn, """
        SELECT v.vehicle_id AS id,v.registration_reference,
               v.make_model,v.vehicle_type,
               ae.external_reference AS associated_entity,
               NULL::text AS last_seen
        FROM case_vehicles cv
        JOIN vehicles v ON v.vehicle_id=cv.vehicle_id
        LEFT JOIN entity_vehicles ev ON ev.vehicle_id=v.vehicle_id
        LEFT JOIN entities ae ON ae.entity_id=ev.entity_id
        WHERE cv.case_id=%(case_id)s
        ORDER BY v.vehicle_id
    """, {"case_id": case_id})

    relationships = fetch_all(conn, """
        SELECT er.relationship_id AS id,
               se.external_reference AS source,
               re.external_reference AS target,
               rt.type_name AS type,
               er.strength_score AS strength,
               'FACT' AS kind
        FROM entity_relationships er
        JOIN relationship_types rt ON rt.relationship_type_id=er.relationship_type_id
        JOIN entities se ON se.entity_id=er.source_entity_id
        JOIN entities re ON re.entity_id=er.target_entity_id
        JOIN case_entities cse ON cse.entity_id=er.source_entity_id AND cse.case_id=%(case_id)s
        JOIN case_entities cte ON cte.entity_id=er.target_entity_id AND cte.case_id=%(case_id)s
        ORDER BY er.strength_score DESC NULLS LAST,er.relationship_id
        LIMIT 300
    """, {"case_id": case_id})

    timeline = fetch_all(conn, """
        SELECT e.event_id AS id,e.event_time AS time,et.type_name AS type,
               en.external_reference AS entity,l.location_name AS location,
               e.description,e.description AS title,e.attributes
        FROM case_events ce
        JOIN events e ON e.event_id=ce.event_id
        JOIN event_types et ON et.event_type_id=e.event_type_id
        LEFT JOIN entity_events ee ON ee.event_id=e.event_id
        LEFT JOIN entities en ON en.entity_id=ee.entity_id
        LEFT JOIN locations l ON l.location_id=e.location_id
        WHERE ce.case_id=%(case_id)s
        ORDER BY e.event_time
        LIMIT 500
    """, {"case_id": case_id})

    questions = fetch_all(conn, """
        SELECT query_code,question_text,module_name
        FROM investigation_queries ORDER BY query_id
    """)

    stats = {
        "entities": len(entities),
        "events": len(timeline),
        "evidence": len(evidence),
        "communications": len(communications),
        "transactions": len(transactions),
        "vehicles": len(vehicles),
        "locations": len(locations),
        "data_sources": _source_count(conn, case_id),
    }

    return {
        "case": case,
        "entities": entities,
        "evidence": evidence,
        "communications": communications,
        "transactions": transactions,
        "locations": locations,
        "vehicles": vehicles,
        "relationships": relationships,
        "timeline": timeline,
        "investigation_questions": questions,
        "stats": stats,
        "synthesis": None,
        "query": {"question": "", "module": None, "status": "Ready", "sql": None, "rows": []},
    }


def _source_count(conn, case_id: int) -> int:
    row = fetch_one(conn, """
        SELECT COUNT(DISTINCT source) AS count FROM (
            SELECT e.source_reference AS source FROM case_evidence ce JOIN evidence e ON e.evidence_id=ce.evidence_id WHERE ce.case_id=%(case_id)s
            UNION ALL
            SELECT e.source_reference FROM case_events ce JOIN events e ON e.event_id=ce.event_id WHERE ce.case_id=%(case_id)s
            UNION ALL
            SELECT c.source_reference FROM case_communications cc JOIN communications c ON c.communication_id=cc.communication_id WHERE cc.case_id=%(case_id)s
            UNION ALL
            SELECT t.source_reference FROM case_transactions ct JOIN transactions t ON t.transaction_id=ct.transaction_id WHERE ct.case_id=%(case_id)s
        ) s WHERE source IS NOT NULL AND source <> ''
    """, {"case_id": case_id})
    return int(row["count"] if row else 0)
