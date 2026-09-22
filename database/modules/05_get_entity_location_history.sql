-- Q6,Q7
SELECT * FROM (SELECT e.location_id,l.location_name,l.location_type,COUNT(*) visit_count,MIN(e.event_time) first_visit,MAX(e.event_time) last_visit,
AVG(e.confidence_score) avg_event_confidence,(CAST(MAX(e.event_time) AS DATE)-CAST(MIN(e.event_time) AS DATE))*86400 observed_span_seconds
FROM entity_events ee JOIN events e ON e.event_id=ee.event_id JOIN locations l ON l.location_id=e.location_id
WHERE ee.entity_id=:entity_id AND e.event_time BETWEEN :start_time AND :end_time
GROUP BY e.location_id,l.location_name,l.location_type ORDER BY last_visit DESC,visit_count DESC) WHERE ROWNUM<=:result_limit
