-- Q5,Q8
SELECT * FROM (SELECT ee.entity_id,en.display_name,e.event_id,e.event_time,e.location_id,et.type_name event_type,e.confidence_score
FROM events e JOIN entity_events ee ON ee.event_id=e.event_id JOIN entities en ON en.entity_id=ee.entity_id JOIN event_types et ON et.event_type_id=e.event_type_id
WHERE e.location_id=:location_id AND e.event_time BETWEEN :start_time AND :end_time ORDER BY e.event_time) WHERE ROWNUM<=:result_limit
