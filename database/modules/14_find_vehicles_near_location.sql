-- Q23,Q24,Q25
SELECT * FROM (SELECT vs.sighting_id,vs.vehicle_id,v.make_model,v.registration_reference,vs.location_id,l.location_name,vs.observed_at,vs.confidence_score,
ev.entity_id,en.display_name,ev.relationship_type FROM vehicle_sightings vs JOIN vehicles v ON v.vehicle_id=vs.vehicle_id
LEFT JOIN locations l ON l.location_id=vs.location_id LEFT JOIN entity_vehicles ev ON ev.vehicle_id=vs.vehicle_id LEFT JOIN entities en ON en.entity_id=ev.entity_id
WHERE vs.location_id=:location_id AND vs.observed_at BETWEEN :start_time AND :end_time ORDER BY vs.observed_at) WHERE ROWNUM<=:result_limit
