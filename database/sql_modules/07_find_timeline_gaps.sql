/*
 M07 - Timeline gaps
 Q13
 Oracle 11g compatible: uses analytic LAG, no FETCH FIRST.
 Binds: :v_case_id, :v_entity_id, :v_start_time, :v_end_time, :v_minimum_gap_minutes, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        event_id,
        event_time,
        previous_event_time,
        ROUND((CAST(event_time AS DATE) - CAST(previous_event_time AS DATE)) * 1440, 2) AS gap_minutes
    FROM (
        SELECT
            ev.event_id,
            ev.event_time,
            LAG(ev.event_time) OVER (ORDER BY ev.event_time) AS previous_event_time
        FROM ENTITY_EVENTS ee
        JOIN EVENTS ev ON ev.event_id = ee.event_id
        JOIN CASE_EVENTS ce ON ce.event_id = ee.event_id
                           AND ce.case_id = :v_case_id
        WHERE ee.entity_id = :v_entity_id
          AND ev.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
          AND ev.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
    )
    WHERE previous_event_time IS NOT NULL
      AND (CAST(event_time AS DATE) - CAST(previous_event_time AS DATE)) * 1440 >= NVL(:v_minimum_gap_minutes, 60)
    ORDER BY event_time ASC
)
WHERE ROWNUM <= :v_result_limit;
