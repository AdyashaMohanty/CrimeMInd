/*
 M04 - Common locations visited by multiple entities
 Q09, Q10
 Actual schema: ENTITY_EVENTS -> EVENTS -> CASE_EVENTS.
 Binds: :v_case_id, :v_entity_id, :v_start_time, :v_end_time, :v_minimum_strength, :v_result_limit
 :v_entity_id may be NULL to search for case-wide shared locations.
*/
SELECT *
FROM (
    SELECT
        ev.location_id,
        COUNT(DISTINCT ee.entity_id) AS entity_count,
        COUNT(*) AS event_count,
        MIN(ev.event_time) AS first_seen,
        MAX(ev.event_time) AS last_seen
    FROM ENTITY_EVENTS ee
    JOIN EVENTS ev ON ev.event_id = ee.event_id
    JOIN CASE_EVENTS ce ON ce.event_id = ee.event_id
                       AND ce.case_id = :v_case_id
    WHERE ev.location_id IS NOT NULL
      AND ev.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND ev.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND (:v_entity_id IS NULL OR ee.entity_id = :v_entity_id)
    GROUP BY ev.location_id
    HAVING COUNT(DISTINCT ee.entity_id) >= NVL(:v_minimum_strength, 2)
    ORDER BY entity_count DESC, event_count DESC
)
WHERE ROWNUM <= :v_result_limit;
