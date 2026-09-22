-- Q2
SELECT * FROM (SELECT c.communication_id,c.start_time,c.end_time,c.duration_seconds,c.status,ct.type_name communication_type,c.sender_entity_id,c.receiver_entity_id,
COUNT(*) OVER() total_matching_records,ROW_NUMBER() OVER(ORDER BY c.start_time) temporal_rank
FROM communications c JOIN communication_types ct ON ct.communication_type_id=c.communication_type_id
WHERE ((c.sender_entity_id=:entity_a AND c.receiver_entity_id=:entity_b) OR (c.sender_entity_id=:entity_b AND c.receiver_entity_id=:entity_a))
AND c.start_time BETWEEN :start_time AND :end_time ORDER BY c.start_time) WHERE ROWNUM<=:result_limit
