-- Q9,Q10
SELECT * FROM (SELECT e.location_id,l.location_name,COUNT(DISTINCT ee.entity_id) distinct_entities,COUNT(*) visit_events,MIN(e.event_time) first_seen,MAX(e.event_time) last_seen
FROM events e JOIN entity_events ee ON ee.event_id=e.event_id JOIN locations l ON l.location_id=e.location_id
WHERE ee.entity_id IN (:entity_ids) AND e.event_time BETWEEN :start_time AND :end_time
GROUP BY e.location_id,l.location_name HAVING COUNT(DISTINCT ee.entity_id)>=:minimum_entities
ORDER BY distinct_entities DESC,visit_events DESC) WHERE ROWNUM<=:result_limit
