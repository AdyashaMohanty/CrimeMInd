SET PAGESIZE 100
SET LINESIZE 200
SET VERIFY OFF
SET FEEDBACK ON

PROMPT ============================================================
PROMPT CRIMEMIND DATABASE VALIDATION
PROMPT ============================================================


PROMPT
PROMPT 1. CASE
PROMPT ------------------------------------------------------------

SELECT
    case_id,
    case_reference,
    title,
    status
FROM investigation_cases;


PROMPT
PROMPT 2. CORE DATA COUNTS
PROMPT ------------------------------------------------------------

SELECT 'COMMUNICATIONS' AS data_set, COUNT(*) AS row_count
FROM communications
UNION ALL
SELECT 'ENTITIES', COUNT(*)
FROM entities
UNION ALL
SELECT 'ENTITY_EVENTS', COUNT(*)
FROM entity_events
UNION ALL
SELECT 'ENTITY_RELATIONSHIPS', COUNT(*)
FROM entity_relationships
UNION ALL
SELECT 'EVIDENCE', COUNT(*)
FROM evidence
UNION ALL
SELECT 'LOCATIONS', COUNT(*)
FROM locations
UNION ALL
SELECT 'TRANSACTIONS', COUNT(*)
FROM transactions
UNION ALL
SELECT 'VEHICLES', COUNT(*)
FROM vehicles
UNION ALL
SELECT 'VEHICLE_SIGHTINGS', COUNT(*)
FROM vehicle_sightings
ORDER BY 1;


PROMPT
PROMPT 3. APPLICATION CASE MAPPINGS
PROMPT ------------------------------------------------------------

SELECT 'CASE_ENTITIES' AS mapping_table, COUNT(*) AS row_count
FROM case_entities
UNION ALL
SELECT 'CASE_LOCATIONS', COUNT(*)
FROM case_locations
UNION ALL
SELECT 'CASE_VEHICLES', COUNT(*)
FROM case_vehicles
UNION ALL
SELECT 'CASE_EVENTS', COUNT(*)
FROM case_events
UNION ALL
SELECT 'CASE_EVIDENCE', COUNT(*)
FROM case_evidence
UNION ALL
SELECT 'CASE_COMMUNICATIONS', COUNT(*)
FROM case_communications
UNION ALL
SELECT 'CASE_TRANSACTIONS', COUNT(*)
FROM case_transactions
ORDER BY 1;


PROMPT
PROMPT 4. INVESTIGATION QUESTIONS
PROMPT ------------------------------------------------------------

SELECT
    COUNT(*) AS investigation_question_count
FROM investigation_queries;


PROMPT
PROMPT 5. SQL MODULES
PROMPT ------------------------------------------------------------

SELECT
    COUNT(*) AS sql_module_count
FROM sql_modules;


PROMPT
PROMPT 6. QUESTION -> MODULE MAPPING
PROMPT ------------------------------------------------------------

SELECT
    COUNT(*) AS question_module_mappings
FROM query_modules;


PROMPT
PROMPT 7. EVIDENCE TYPES
PROMPT ------------------------------------------------------------

SELECT
    et.type_name AS evidence_type,
    COUNT(e.evidence_id) AS evidence_count
FROM evidence_types et
LEFT JOIN evidence e
    ON e.evidence_type_id = et.evidence_type_id
GROUP BY et.type_name
ORDER BY et.type_name;


PROMPT
PROMPT 8. ENTITY TYPES
PROMPT ------------------------------------------------------------

SELECT
    et.type_name AS entity_type,
    COUNT(e.entity_id) AS entity_count
FROM entity_types et
LEFT JOIN entities e
    ON e.entity_type_id = et.entity_type_id
GROUP BY et.type_name
ORDER BY et.type_name;


PROMPT
PROMPT 9. EVENT TYPES
PROMPT ------------------------------------------------------------

SELECT
    et.type_name AS event_type,
    COUNT(ee.entity_event_id) AS event_count
FROM event_types et
LEFT JOIN entity_events ee
    ON ee.event_id IN (
        SELECT event_id
        FROM entity_events
    )
GROUP BY et.type_name
ORDER BY et.type_name;


PROMPT
PROMPT 10. COMMUNICATION TYPES
PROMPT ------------------------------------------------------------

SELECT
    ct.type_name AS communication_type,
    COUNT(c.communication_id) AS communication_count
FROM communication_types ct
LEFT JOIN communications c
    ON c.communication_type_id = ct.communication_type_id
GROUP BY ct.type_name
ORDER BY ct.type_name;


PROMPT
PROMPT 11. DATA INTEGRITY CHECKS
PROMPT ------------------------------------------------------------

SELECT
    'ORPHAN CASE ENTITIES' AS check_name,
    COUNT(*) AS problem_count
FROM case_entities ce
LEFT JOIN entities e
    ON e.entity_id = ce.entity_id
WHERE e.entity_id IS NULL

UNION ALL

SELECT
    'ORPHAN CASE LOCATIONS',
    COUNT(*)
FROM case_locations cl
LEFT JOIN locations l
    ON l.location_id = cl.location_id
WHERE l.location_id IS NULL

UNION ALL

SELECT
    'ORPHAN CASE VEHICLES',
    COUNT(*)
FROM case_vehicles cv
LEFT JOIN vehicles v
    ON v.vehicle_id = cv.vehicle_id
WHERE v.vehicle_id IS NULL

UNION ALL

SELECT
    'ORPHAN CASE EVENTS',
    COUNT(*)
FROM case_events ce
LEFT JOIN entity_events ee
    ON ee.event_id = ce.event_id
WHERE ee.event_id IS NULL

UNION ALL

SELECT
    'ORPHAN CASE EVIDENCE',
    COUNT(*)
FROM case_evidence ce
LEFT JOIN evidence e
    ON e.evidence_id = ce.evidence_id
WHERE e.evidence_id IS NULL;


PROMPT
PROMPT 12. EVALUATION-ONLY SAFETY CHECK
PROMPT ------------------------------------------------------------

SELECT
    COUNT(*) AS ground_truth_operational_rows
FROM evidence
WHERE LOWER(NVL(source_reference, '')) LIKE '%ground_truth%';


PROMPT
PROMPT 13. APPLICATION TABLE STATUS
PROMPT ------------------------------------------------------------

SELECT
    'INVESTIGATION_QUERIES' AS table_name,
    COUNT(*) AS row_count
FROM investigation_queries
UNION ALL
SELECT
    'SQL_MODULES',
    COUNT(*)
FROM sql_modules
UNION ALL
SELECT
    'QUERY_MODULES',
    COUNT(*)
FROM query_modules
ORDER BY 1;


PROMPT
PROMPT ============================================================
PROMPT VALIDATION COMPLETE
PROMPT ============================================================