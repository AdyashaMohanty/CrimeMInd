/*
 M15 - Financial transactions
 Q26-Q30
 Binds: :v_case_id, :v_entity_id, :v_entity_id_2, :v_start_time, :v_end_time, :v_minimum_amount, :v_result_limit
*/
SELECT *
FROM (
    SELECT
        t.transaction_id,
        t.sender_entity_id,
        t.receiver_entity_id,
        t.amount,
        t.currency,
        t.transaction_time,
        t.transaction_type,
        t.status,
        t.source_reference
    FROM TRANSACTIONS t
    JOIN CASE_TRANSACTIONS ct ON ct.transaction_id = t.transaction_id
                             AND ct.case_id = :v_case_id
    WHERE (t.sender_entity_id = :v_entity_id OR t.receiver_entity_id = :v_entity_id)
      AND (:v_entity_id_2 IS NULL
           OR (t.sender_entity_id = :v_entity_id_2 OR t.receiver_entity_id = :v_entity_id_2))
      AND t.transaction_time >= TO_TIMESTAMP_TZ(:v_start_time || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND t.transaction_time <  TO_TIMESTAMP_TZ(:v_end_time   || ' 00:00:00 +05:30','DD-MON-YYYY HH24:MI:SS TZH:TZM')
      AND NVL(t.amount,0) >= NVL(:v_minimum_amount,0)
    ORDER BY t.transaction_time DESC, t.amount DESC
)
WHERE ROWNUM <= :v_result_limit;
