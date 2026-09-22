/*
 M02 - Communication between two entities
 Q02
 Binds: :v_case_id, :v_entity_id_1, :v_entity_id_2, :v_start_time, :v_end_time, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        c.communication_id,
        c.sender_entity_id,
        c.receiver_entity_id,
        c.communication_type,
        e.event_time,
        c.source_reference
    FROM COMMUNICATIONS c
    JOIN EVENTS e ON e.event_id = c.event_id
    JOIN CASE_COMMUNICATIONS cc ON cc.communication_id = c.communication_id
                               AND cc.case_id = :v_case_id
    WHERE ((c.sender_entity_id = :v_entity_id_1 AND c.receiver_entity_id = :v_entity_id_2)
        OR (c.sender_entity_id = :v_entity_id_2 AND c.receiver_entity_id = :v_entity_id_1))
      AND e.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND e.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
    ORDER BY e.event_time DESC
)
WHERE ROWNUM <= :v_result_limit;
