/*
 M01 - Recent contacts / repeated communication
 Q01, Q03, Q04
 Binds: :v_case_id, :v_entity_id, :v_start_time, :v_end_time, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        c.other_entity_id AS contact_entity_id,
        COUNT(*) AS communication_count,
        MAX(c.event_time) AS last_contact_time
    FROM (
        SELECT
            CASE WHEN c.sender_entity_id = :v_entity_id
                 THEN c.receiver_entity_id ELSE c.sender_entity_id END AS other_entity_id,
            e.event_time
        FROM COMMUNICATIONS c
        JOIN EVENTS e ON e.event_id = c.event_id
        JOIN CASE_COMMUNICATIONS cc ON cc.communication_id = c.communication_id
                                   AND cc.case_id = :v_case_id
        WHERE (c.sender_entity_id = :v_entity_id OR c.receiver_entity_id = :v_entity_id)
          AND e.event_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
          AND e.event_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
    ) c
    GROUP BY c.other_entity_id
    ORDER BY communication_count DESC, last_contact_time DESC
)
WHERE ROWNUM <= :v_result_limit;
