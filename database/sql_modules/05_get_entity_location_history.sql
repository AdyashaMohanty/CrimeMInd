/*
 M05 - Entity location history
 Q06, Q07
 Binds: :v_case_id, :v_entity_id, :v_start_time, :v_end_time, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        ee.entity_id,
        ev.event_id,
        ev.location_id,
        ev.event_time,
        ev.end_time,
        ev.event_type_id,
        ev.source_reference
    FROM ENTITY_EVENTS ee
    JOIN EVENTS ev ON ev.event_id = ee.event_id
    JOIN CASE_EVENTS ce ON ce.event_id = ee.event_id
                       AND ce.case_id = :v_case_id
    WHERE ee.entity_id = :v_entity_id
      AND ev.location_id IS NOT NULL
      AND ev.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND ev.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
    ORDER BY ev.event_time DESC
)
WHERE ROWNUM <= :v_result_limit;
