-- Q1,Q3,Q4
SELECT * FROM (SELECT CASE WHEN c.sender_entity_id=:entity_id THEN c.receiver_entity_id ELSE c.sender_entity_id END contact_entity_id,e.display_name contact_name,
COUNT(*) communication_count,MIN(c.start_time) first_contact,MAX(c.start_time) last_contact,COUNT(DISTINCT TRUNC(c.start_time)) active_days,
AVG(c.duration_seconds) avg_duration_seconds
FROM communications c JOIN entities e ON e.entity_id=CASE WHEN c.sender_entity_id=:entity_id THEN c.receiver_entity_id ELSE c.sender_entity_id END
WHERE (c.sender_entity_id=:entity_id OR c.receiver_entity_id=:entity_id) AND c.start_time BETWEEN :start_time AND :end_time
GROUP BY CASE WHEN c.sender_entity_id=:entity_id THEN c.receiver_entity_id ELSE c.sender_entity_id END,e.display_name
ORDER BY communication_count DESC,last_contact DESC) WHERE ROWNUM<=:result_limit
