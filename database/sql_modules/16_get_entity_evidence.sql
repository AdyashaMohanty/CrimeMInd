/*
 M16 - Evidence associated with an entity or event
 Q31: What evidence is associated with a specified entity?
 Q32: What evidence is associated with a specified event or incident?

 Binds:
 :v_case_id
 :v_entity_id
 :v_event_id
 :v_result_limit

 Evidence-to-entity links come from EVIDENCE_ENTITIES.
 Evidence-to-event links come from EVIDENCE_EVENTS.
*/
SELECT *
FROM (
    SELECT
        e.evidence_id,
        et.type_name AS evidence_type,
        e.collected_at,
        e.source_reference,
        e.base_confidence,
        et.base_weight,
        (e.base_confidence * et.base_weight) AS evidence_score,
        e.description,
        ee.entity_id,
        ee.association_confidence,
        ee.relation_role,
        eev.event_id
    FROM EVIDENCE e
    JOIN CASE_EVIDENCE ce
      ON ce.case_id = :v_case_id
     AND ce.evidence_id = e.evidence_id
    JOIN EVIDENCE_TYPES et
      ON et.evidence_type_id = e.evidence_type_id
    LEFT JOIN EVIDENCE_ENTITIES ee
      ON ee.evidence_id = e.evidence_id
    LEFT JOIN EVIDENCE_EVENTS eev
      ON eev.evidence_id = e.evidence_id
    WHERE (:v_entity_id IS NULL OR ee.entity_id = :v_entity_id)
      AND (:v_event_id IS NULL OR eev.event_id = :v_event_id)
    ORDER BY (e.base_confidence * et.base_weight) DESC,
             e.collected_at DESC NULLS LAST,
             e.evidence_id
)
WHERE ROWNUM <= :v_result_limit;
