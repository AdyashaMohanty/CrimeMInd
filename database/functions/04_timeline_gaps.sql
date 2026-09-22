CREATE OR REPLACE FUNCTION find_timeline_gap_seconds(
 p_entity_id NUMBER,p_start TIMESTAMP WITH TIME ZONE,p_end TIMESTAMP WITH TIME ZONE)
RETURN SYS_REFCURSOR
IS c SYS_REFCURSOR;
BEGIN
 OPEN c FOR
 SELECT previous_event_id,next_event_id,
        (CAST(next_event_time AS DATE)-CAST(previous_event_time AS DATE))*86400 gap_seconds
 FROM (
   SELECT e.event_id previous_event_id,LEAD(e.event_id) OVER(ORDER BY e.event_time) next_event_id,
          e.event_time previous_event_time,LEAD(e.event_time) OVER(ORDER BY e.event_time) next_event_time
   FROM entity_events ee JOIN events e ON e.event_id=ee.event_id
   WHERE ee.entity_id=p_entity_id AND e.event_time BETWEEN p_start AND p_end
 )
 WHERE next_event_time IS NOT NULL ORDER BY gap_seconds DESC;
 RETURN c;
END;
/
