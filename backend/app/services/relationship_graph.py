from app.db.sql import fetch_all


def build_relationship_graph(conn, case_id: int):
    """Build an evidence-backed graph using only records belonging to one case."""
    nodes = {}
    edges = []
    edge_keys = set()

    def add_node(node_id, label, node_type):
        if node_id is None:
            return
        key = str(node_id)
        nodes.setdefault(key, {
            "id": key,
            "label": label or key,
            "type": node_type,
        })

    def add_edge(edge_id, source, target, relationship, classification,
                 source_type, source_id, timestamp=None, strength=None):
        if source is None or target is None or str(source) == str(target):
            return
        source, target = str(source), str(target)
        key = (source, target, relationship, str(source_id))
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({
            "id": str(edge_id),
            "source": source,
            "target": target,
            "relationship": relationship,
            "classification": classification,
            "source_type": source_type,
            "source_id": str(source_id) if source_id is not None else None,
            "timestamp": timestamp,
            "strength": float(strength) if strength is not None else None,
        })

    # Case entities
    rows = fetch_all(conn, """
        SELECT e.entity_id, e.external_reference, e.display_name, et.type_name
        FROM case_entities ce
        JOIN entities e ON e.entity_id = ce.entity_id
        JOIN entity_types et ON et.entity_type_id = e.entity_type_id
        WHERE ce.case_id=:case_id
        ORDER BY e.entity_id
    """, {"case_id": case_id})
    entity_ids = set()
    for r in rows:
        entity_ids.add(r["entity_id"])
        add_node(r["external_reference"] or r["entity_id"], r["display_name"],
                 "PERSON" if "PERSON" in r["type_name"].upper() else r["type_name"])

    # Case locations
    rows = fetch_all(conn, """
        SELECT l.location_id, l.external_reference, l.location_name, l.location_type
        FROM case_locations cl
        JOIN locations l ON l.location_id=cl.location_id
        WHERE cl.case_id=:case_id
        ORDER BY l.location_id
    """, {"case_id": case_id})
    location_ids = set()
    for r in rows:
        location_ids.add(r["location_id"])
        add_node(r["external_reference"] or r["location_id"], r["location_name"], "LOCATION")

    # Case vehicles
    rows = fetch_all(conn, """
        SELECT v.vehicle_id, v.external_reference,
               COALESCE(v.registration_reference, v.make_model, TO_CHAR(v.vehicle_id)) AS label
        FROM case_vehicles cv
        JOIN vehicles v ON v.vehicle_id=cv.vehicle_id
        WHERE cv.case_id=:case_id
        ORDER BY v.vehicle_id
    """, {"case_id": case_id})
    vehicle_ids = set()
    for r in rows:
        vehicle_ids.add(r["vehicle_id"])
        add_node(r["external_reference"] or r["vehicle_id"], r["label"], "VEHICLE")

    # Case evidence
    rows = fetch_all(conn, """
        SELECT e.evidence_id, et.type_name,
               COALESCE(NULLIF(e.description,''), 'Evidence ' || TO_CHAR(e.evidence_id)) AS label
        FROM case_evidence ce
        JOIN evidence e ON e.evidence_id=ce.evidence_id
        JOIN evidence_types et ON et.evidence_type_id=e.evidence_type_id
        WHERE ce.case_id=:case_id
        ORDER BY e.evidence_id
    """, {"case_id": case_id})
    evidence_ids = set()
    for r in rows:
        evidence_ids.add(r["evidence_id"])
        add_node(f"EVIDENCE-{r['evidence_id']}", r["label"], "EVIDENCE")

    # Direct recorded entity relationships
    rows = fetch_all(conn, """
        SELECT er.relationship_id,
               s.external_reference AS source,
               t.external_reference AS target,
               rt.type_name AS relationship,
               er.strength_score, er.valid_from
        FROM entity_relationships er
        JOIN relationship_types rt ON rt.relationship_type_id=er.relationship_type_id
        JOIN entities s ON s.entity_id=er.source_entity_id
        JOIN entities t ON t.entity_id=er.target_entity_id
        WHERE er.source_entity_id IN (
            SELECT entity_id FROM case_entities WHERE case_id=:case_id
        )
        AND er.target_entity_id IN (
            SELECT entity_id FROM case_entities WHERE case_id=:case_id
        )
        ORDER BY er.relationship_id
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"REL-{r['relationship_id']}", r["source"], r["target"],
                 r["relationship"], "FACT", "entity_relationship",
                 r["relationship_id"], r["valid_from"], r["strength_score"])

    # Communications
    rows = fetch_all(conn, """
        SELECT c.communication_id, s.external_reference AS source,
               t.external_reference AS target, c.start_time
        FROM case_communications cc
        JOIN communications c ON c.communication_id=cc.communication_id
        JOIN entities s ON s.entity_id=c.sender_entity_id
        JOIN entities t ON t.entity_id=c.receiver_entity_id
        WHERE cc.case_id=:case_id
        ORDER BY c.start_time
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"COM-{r['communication_id']}", r["source"], r["target"],
                 "COMMUNICATED_WITH", "FACT", "communication",
                 r["communication_id"], r["start_time"])

    # Transactions
    rows = fetch_all(conn, """
        SELECT t.transaction_id, s.external_reference AS source,
               r.external_reference AS target, t.transaction_time
        FROM case_transactions ct
        JOIN transactions t ON t.transaction_id=ct.transaction_id
        JOIN entities s ON s.entity_id=t.sender_entity_id
        JOIN entities r ON r.entity_id=t.receiver_entity_id
        WHERE ct.case_id=:case_id
        ORDER BY t.transaction_time
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"TX-{r['transaction_id']}", r["source"], r["target"],
                 "FINANCIAL_TRANSFER", "FACT", "transaction",
                 r["transaction_id"], r["transaction_time"])

    # Entity ↔ vehicle association
    rows = fetch_all(conn, """
        SELECT ev.entity_vehicle_id, e.external_reference AS entity_ref,
               v.external_reference AS vehicle_ref, ev.relationship_type
        FROM entity_vehicles ev
        JOIN entities e ON e.entity_id=ev.entity_id
        JOIN vehicles v ON v.vehicle_id=ev.vehicle_id
        WHERE ev.entity_id IN (SELECT entity_id FROM case_entities WHERE case_id=:case_id)
          AND ev.vehicle_id IN (SELECT vehicle_id FROM case_vehicles WHERE case_id=:case_id)
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"EV-{r['entity_vehicle_id']}", r["entity_ref"], r["vehicle_ref"],
                 r["relationship_type"] or "ASSOCIATED_WITH", "FACT",
                 "entity_vehicle", r["entity_vehicle_id"])

    # Vehicle ↔ location sightings
    rows = fetch_all(conn, """
        SELECT vs.sighting_id, v.external_reference AS vehicle_ref,
               l.external_reference AS location_ref, vs.observed_at
        FROM vehicle_sightings vs
        JOIN vehicles v ON v.vehicle_id=vs.vehicle_id
        JOIN locations l ON l.location_id=vs.location_id
        WHERE vs.vehicle_id IN (SELECT vehicle_id FROM case_vehicles WHERE case_id=:case_id)
          AND vs.location_id IN (SELECT location_id FROM case_locations WHERE case_id=:case_id)
        ORDER BY vs.observed_at
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"SIGHTING-{r['sighting_id']}", r["vehicle_ref"], r["location_ref"],
                 "OBSERVED_AT", "FACT", "vehicle_sighting", r["sighting_id"], r["observed_at"])

    # Entity ↔ evidence
    rows = fetch_all(conn, """
        SELECT ee.evidence_entity_id, e.external_reference AS entity_ref,
               ee.evidence_id, ee.association_confidence
        FROM evidence_entities ee
        JOIN entities e ON e.entity_id=ee.entity_id
        WHERE ee.entity_id IN (SELECT entity_id FROM case_entities WHERE case_id=:case_id)
          AND ee.evidence_id IN (SELECT evidence_id FROM case_evidence WHERE case_id=:case_id)
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"EEL-{r['evidence_entity_id']}", r["entity_ref"],
                 f"EVIDENCE-{r['evidence_id']}", "SUPPORTED_BY_EVIDENCE", "FACT",
                 "evidence_entity", r["evidence_entity_id"],
                 strength=r["association_confidence"])

    # Entity ↔ location from recorded events
    rows = fetch_all(conn, """
        SELECT ee.entity_event_id, e.entity_id, en.external_reference AS entity_ref,
               ev.event_id, l.external_reference AS location_ref, ev.event_time
        FROM entity_events ee
        JOIN entities en ON en.entity_id=ee.entity_id
        JOIN events ev ON ev.event_id=ee.event_id
        JOIN locations l ON l.location_id=ev.location_id
        JOIN case_events ce ON ce.event_id=ev.event_id
        WHERE ce.case_id=:case_id
          AND ee.entity_id IN (SELECT entity_id FROM case_entities WHERE case_id=:case_id)
          AND ev.location_id IN (SELECT location_id FROM case_locations WHERE case_id=:case_id)
        ORDER BY ev.event_time
    """, {"case_id": case_id})
    for r in rows:
        add_edge(f"EVENTLOC-{r['entity_event_id']}", r["entity_ref"], r["location_ref"],
                 "RECORDED_AT", "FACT", "event", r["event_id"], r["event_time"])

    # Correlation: entities recorded at the same location within 30 minutes.
    rows = fetch_all(conn, """
        SELECT a.entity_ref AS source, b.entity_ref AS target,
               a.location_ref, a.event_id AS source_event, b.event_id AS target_event,
               a.event_time AS source_time
        FROM (
            SELECT ee.entity_id, en.external_reference AS entity_ref,
                   ev.event_id, ev.event_time, l.location_id,
                   l.external_reference AS location_ref
            FROM case_events ce
            JOIN events ev ON ev.event_id=ce.event_id
            JOIN entity_events ee ON ee.event_id=ev.event_id
            JOIN entities en ON en.entity_id=ee.entity_id
            JOIN locations l ON l.location_id=ev.location_id
            WHERE ce.case_id=:case_id
        ) a
        JOIN (
            SELECT ee.entity_id, en.external_reference AS entity_ref,
                   ev.event_id, ev.event_time, l.location_id
            FROM case_events ce
            JOIN events ev ON ev.event_id=ce.event_id
            JOIN entity_events ee ON ee.event_id=ev.event_id
            JOIN entities en ON en.entity_id=ee.entity_id
            JOIN locations l ON l.location_id=ev.location_id
            WHERE ce.case_id=:case_id
        ) b ON a.location_id=b.location_id
           AND a.entity_id < b.entity_id
           AND ABS(ABS((CAST(a.event_time AS DATE)-CAST(b.event_time AS DATE))*86400)) <= 1800
    """, {"case_id": case_id})
    for i, r in enumerate(rows, 1):
        add_edge(f"CORR-LOC-{i}", r["source"], r["target"],
                 "CO_LOCATED_WITHIN_30_MIN", "CORRELATED", "event_pair",
                 f"{r['source_event']}-{r['target_event']}", r["source_time"])

    # Inference: two case entities share the same evidence record.
    rows = fetch_all(conn, """
        SELECT a.entity_ref AS source, b.entity_ref AS target,
               a.evidence_id, a.evidence_entity_id AS source_link,
               b.evidence_entity_id AS target_link
        FROM (
            SELECT ee.evidence_entity_id, ee.evidence_id, e.external_reference AS entity_ref
            FROM evidence_entities ee
            JOIN entities e ON e.entity_id=ee.entity_id
            WHERE ee.evidence_id IN (SELECT evidence_id FROM case_evidence WHERE case_id=:case_id)
              AND ee.entity_id IN (SELECT entity_id FROM case_entities WHERE case_id=:case_id)
        ) a
        JOIN (
            SELECT ee.evidence_entity_id, ee.evidence_id, e.external_reference AS entity_ref
            FROM evidence_entities ee
            JOIN entities e ON e.entity_id=ee.entity_id
            WHERE ee.evidence_id IN (SELECT evidence_id FROM case_evidence WHERE case_id=:case_id)
              AND ee.entity_id IN (SELECT entity_id FROM case_entities WHERE case_id=:case_id)
        ) b ON a.evidence_id=b.evidence_id
          AND a.entity_ref < b.entity_ref
    """, {"case_id": case_id})
    for i, r in enumerate(rows, 1):
        add_edge(f"INF-EVID-{i}", r["source"], r["target"],
                 "SHARED_EVIDENCE", "INFERRED", "evidence",
                 r["evidence_id"])

    return {
        "case_id": case_id,
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {"nodes": len(nodes), "edges": len(edges)},
    }
