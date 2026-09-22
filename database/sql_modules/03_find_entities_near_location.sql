/*
 M03 - Entities recorded at a specified location
 Q05, Q08
 Actual schema: ENTITY_EVENTS -> EVENTS -> CASE_EVENTS.
 Binds: :v_case_id, :v_location_id, :v_start_time, :v_end_time, :v_result_limit
*/
SELECT *
FROM (
    SELECT DISTINCT
        ee.entity_id,
        ee.event_id,
        ee.role,
        ev.event_type_id,
        ev.event_time,
        ev.end_time,
        ev.location_id,
        ev.source_reference,
        ev.confidence_score
    FROM ENTITY_EVENTS ee
    JOIN EVENTS ev ON ev.event_id = ee.event_id
    JOIN CASE_EVENTS ce ON ce.event_id = ee.event_id
                       AND ce.case_id = :v_case_id
    WHERE ev.location_id = :v_location_id
      AND ev.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND ev.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
    ORDER BY ev.event_time DESC
)
WHERE ROWNUM <= :v_result_limit;
