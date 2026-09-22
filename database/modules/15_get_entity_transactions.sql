-- Q26,Q27,Q28,Q29,Q30
WITH tx AS (SELECT t.*,s.display_name sender_name,r.display_name receiver_name FROM transactions t JOIN entities s ON s.entity_id=t.sender_entity_id JOIN entities r ON r.entity_id=t.receiver_entity_id
WHERE (t.sender_entity_id=:entity_id OR t.receiver_entity_id=:entity_id) AND t.transaction_time BETWEEN :start_time AND :end_time)
SELECT * FROM (SELECT tx.*,COUNT(*) OVER() total_matching_transactions FROM tx ORDER BY transaction_time DESC) WHERE ROWNUM<=:result_limit
