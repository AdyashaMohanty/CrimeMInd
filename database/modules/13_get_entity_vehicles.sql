-- Q22
SELECT * FROM (SELECT v.vehicle_id,v.vehicle_type,v.make_model,v.registration_reference,ev.relationship_type,ev.valid_from,ev.valid_to
FROM entity_vehicles ev JOIN vehicles v ON v.vehicle_id=ev.vehicle_id WHERE ev.entity_id=:entity_id
AND (ev.valid_to IS NULL OR ev.valid_to>=:start_time) AND (ev.valid_from IS NULL OR ev.valid_from<=:end_time)
ORDER BY v.vehicle_id) WHERE ROWNUM<=:result_limit
