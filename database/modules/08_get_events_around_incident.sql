-- Q14,Q15,Q16
SELECT * FROM (WITH candidates AS (
SELECT e.event_id,e.event_time,e.location_id,l.location_name,et.type_name event_type,e.confidence_score,e.description,
CASE WHEN e.event_time<i.incident_time THEN 'BEFORE' WHEN e.event_time>i.incident_time THEN 'AFTER' ELSE 'AT' END temporal_position,
ABS((CAST(e.event_time AS DATE)-CAST(i.incident_time AS DATE))*86400) seconds_from_incident
FROM investigation_cases i JOIN events incident ON incident.event_id=:incident_event_id
JOIN events e ON e.event_time BETWEEN i.incident_time-NUMTODSINTERVAL(:window_before,'SECOND') AND i.incident_time+NUMTODSINTERVAL(:window_after,'SECOND')
LEFT JOIN locations l ON l.location_id=e.location_id JOIN event_types et ON et.event_type_id=e.event_type_id
WHERE i.case_id=:case_id AND e.event_id<>:incident_event_id)
SELECT c.*,ROW_NUMBER() OVER(PARTITION BY temporal_position ORDER BY seconds_from_incident) temporal_rank FROM candidates c
ORDER BY seconds_from_incident) WHERE ROWNUM<=:result_limit
