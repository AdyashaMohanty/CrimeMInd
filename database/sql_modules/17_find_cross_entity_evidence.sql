/*
 M17 - Cross-entity / multi-type evidence analysis

 Supports:
 Q33: Which evidence items connect multiple entities?
 Q36: Which entities are supported by multiple independent evidence types?
 Q37: Which evidence items independently corroborate the same entity or event?

 Binds:
 :v_case_id
 :v_analysis_type
 :v_minimum_entity_count
 :v_minimum_evidence_types
 :v_result_limit

 Analysis types:
 CROSS_ENTITY
 MULTI_TYPE_ENTITY
 CORROBORATION
*/


/* ============================================================
   Q33 - Evidence items connecting multiple entities
   ============================================================ */

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
        COUNT(DISTINCT ee.entity_id) AS entity_count,
        DBMS_LOB.SUBSTR(e.description, 4000, 1) AS description
    FROM EVIDENCE e
    JOIN CASE_EVIDENCE ce
      ON ce.case_id = :v_case_id
     AND ce.evidence_id = e.evidence_id
    JOIN EVIDENCE_TYPES et
      ON et.evidence_type_id = e.evidence_type_id
    JOIN EVIDENCE_ENTITIES ee
      ON ee.evidence_id = e.evidence_id
    WHERE :v_analysis_type = 'CROSS_ENTITY'
    GROUP BY
        e.evidence_id,
        et.type_name,
        e.collected_at,
        e.source_reference,
        e.base_confidence,
        et.base_weight,
        DBMS_LOB.SUBSTR(e.description, 4000, 1)
    HAVING COUNT(DISTINCT ee.entity_id)
           >= NVL(:v_minimum_entity_count, 2)
    ORDER BY
        entity_count DESC,
        evidence_score DESC,
        e.evidence_id
)
WHERE ROWNUM <= :v_result_limit;


/* ============================================================
   Q36 - Entities supported by multiple independent evidence types
   ============================================================ */

SELECT *
FROM (
    SELECT
        ee.entity_id,
        COUNT(DISTINCT e.evidence_id) AS evidence_count,
        COUNT(DISTINCT et.type_name) AS evidence_type_count
    FROM EVIDENCE e
    JOIN CASE_EVIDENCE ce
      ON ce.case_id = :v_case_id
     AND ce.evidence_id = e.evidence_id
    JOIN EVIDENCE_TYPES et
      ON et.evidence_type_id = e.evidence_type_id
    JOIN EVIDENCE_ENTITIES ee
      ON ee.evidence_id = e.evidence_id
    WHERE :v_analysis_type = 'MULTI_TYPE_ENTITY'
    GROUP BY
        ee.entity_id
    HAVING COUNT(DISTINCT et.type_name)
           >= NVL(:v_minimum_evidence_types, 2)
    ORDER BY
        evidence_type_count DESC,
        evidence_count DESC,
        ee.entity_id
)
WHERE ROWNUM <= :v_result_limit;


/* ============================================================
   Q37 - Evidence items independently corroborating the same
         entity

   This implementation identifies entities supported by multiple
   evidence items and multiple evidence types.

   Event-level corroboration is handled separately because
   EVIDENCE_EVENTS must be incorporated into that analysis.
   ============================================================ */

SELECT *
FROM (
    SELECT
        ee.entity_id,
        COUNT(DISTINCT e.evidence_id) AS evidence_count,
        COUNT(DISTINCT et.type_name) AS evidence_type_count
    FROM EVIDENCE e
    JOIN CASE_EVIDENCE ce
      ON ce.case_id = :v_case_id
     AND ce.evidence_id = e.evidence_id
    JOIN EVIDENCE_TYPES et
      ON et.evidence_type_id = e.evidence_type_id
    JOIN EVIDENCE_ENTITIES ee
      ON ee.evidence_id = e.evidence_id
    WHERE :v_analysis_type = 'CORROBORATION'
    GROUP BY
        ee.entity_id
    HAVING COUNT(DISTINCT e.evidence_id)
           >= NVL(:v_minimum_entity_count, 2)
       AND COUNT(DISTINCT et.type_name)
           >= NVL(:v_minimum_evidence_types, 2)
    ORDER BY
        evidence_type_count DESC,
        evidence_count DESC,
        ee.entity_id
)
WHERE ROWNUM <= :v_result_limit;