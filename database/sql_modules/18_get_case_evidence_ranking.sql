/*
 M18 - Case evidence ranking
 Q34: Which evidence items have the highest reliability scores?
 Q35: Which entities have the strongest overall evidence associations?
 Q38: Which entities are connected to both a specified entity and a specified location?
 Q39: Which entities have multiple independent links across communications, locations,
      relationships, vehicles, transactions, or evidence?
 Q40: Which entities have the strongest overall association with a specified investigation
      based on combined temporal, spatial, relational, financial, communication, and evidence signals?

 Binds:
 :v_case_id
 :v_entity_id
 :v_location_id
 :v_result_limit

 This module ranks CASE-SCOPED evidence associations. It does not claim guilt,
 and it does not manufacture cross-domain scores where no normalized score exists.
 Evidence score = BASE_CONFIDENCE * EVIDENCE_TYPES.BASE_WEIGHT.
*/
SELECT *
FROM (
    SELECT
        ee.entity_id,
        COUNT(DISTINCT e.evidence_id) AS evidence_count,
        COUNT(DISTINCT e.evidence_type_id) AS evidence_type_count,
        SUM(e.base_confidence * et.base_weight) AS evidence_score,
        MAX(e.base_confidence * et.base_weight) AS strongest_evidence_score
    FROM EVIDENCE e
    JOIN CASE_EVIDENCE ce
      ON ce.case_id = :v_case_id
     AND ce.evidence_id = e.evidence_id
    JOIN EVIDENCE_TYPES et
      ON et.evidence_type_id = e.evidence_type_id
    JOIN EVIDENCE_ENTITIES ee
      ON ee.evidence_id = e.evidence_id
    WHERE (:v_entity_id IS NULL OR ee.entity_id = :v_entity_id)
      AND (
            :v_location_id IS NULL
            OR EXISTS (
                SELECT 1
                FROM EVIDENCE_EVENTS eev
                JOIN EVENTS ev
                  ON ev.event_id = eev.event_id
                WHERE eev.evidence_id = e.evidence_id
                  AND ev.location_id = :v_location_id
            )
          )
    GROUP BY ee.entity_id
    ORDER BY evidence_score DESC, evidence_count DESC, ee.entity_id
)
WHERE ROWNUM <= :v_result_limit;
