/*
 M08 - Events around incident
 Q14, Q15, Q16
 Binds: :v_case_id, :v_incident_event_id, :v_before_minutes, :v_after_minutes, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        ee.entity_id,
        ee.event_id,
        ee.role,
        ev.event_type_id,
        ev.event_time,
        ev.end_time,
        ev.location_id,
        ev.source_reference,
        ev.description
    FROM ENTITY_EVENTS ee
    JOIN EVENTS ev ON ev.event_id = ee.event_id
    JOIN CASE_EVENTS ce ON ce.event_id = ee.event_id
                       AND ce.case_id = :v_case_id
    CROSS JOIN (
        SELECT event_time AS incident_time
        FROM EVENTS
        WHERE event_id = :v_incident_event_id
    ) i
    WHERE ev.event_time >= i.incident_time - NUMTODSINTERVAL(NVL(:v_before_minutes, 60), 'MINUTE')
      AND ev.event_time <= i.incident_time + NUMTODSINTERVAL(NVL(:v_after_minutes, 60), 'MINUTE')
      AND ev.event_id <> :v_incident_event_id
    ORDER BY ev.event_time
)
WHERE ROWNUM <= :v_result_limit;
