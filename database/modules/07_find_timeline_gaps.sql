-- Q13
SELECT * FROM (WITH ordered AS (
SELECT e.event_id,e.event_time,LEAD(e.event_id) OVER(ORDER BY e.event_time) next_event_id,LEAD(e.event_time) OVER(ORDER BY e.event_time) next_event_time
FROM entity_events ee JOIN events e ON e.event_id=ee.event_id WHERE ee.entity_id=:entity_id AND e.event_time BETWEEN :start_time AND :end_time)
SELECT event_id previous_event_id,next_event_id,event_time previous_event_time,next_event_time,
(CAST(next_event_time AS DATE)-CAST(event_time AS DATE))*86400 gap_seconds FROM ordered
WHERE next_event_time IS NOT NULL AND (CAST(next_event_time AS DATE)-CAST(event_time AS DATE))*86400>=:minimum_gap_seconds
ORDER BY gap_seconds DESC) WHERE ROWNUM<=:result_limit
