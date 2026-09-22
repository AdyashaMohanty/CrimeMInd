-- Q11,Q12
SELECT * FROM (SELECT e.event_id,e.event_time,e.end_time,et.type_name event_type,e.location_id,l.location_name,e.confidence_score,e.description,e.attributes
FROM entity_events ee JOIN events e ON e.event_id=ee.event_id JOIN event_types et ON et.event_type_id=e.event_type_id LEFT JOIN locations l ON l.location_id=e.location_id
WHERE ee.entity_id=:entity_id AND e.event_time BETWEEN :start_time AND :end_time ORDER BY e.event_time) WHERE ROWNUM<=:result_limit
