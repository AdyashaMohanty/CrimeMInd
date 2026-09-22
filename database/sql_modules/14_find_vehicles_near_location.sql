/*
 M14 - Vehicle sightings
 Q23: Which vehicles were observed near a specified location during a specified time period?
 Q24: Which entities were associated with a specified vehicle during a specified period?
 Q25: Which vehicles or associated entities appear repeatedly across relevant locations or time periods?

 Binds:
 :v_case_id
 :v_location_id
 :v_vehicle_id
 :v_start_time
 :v_end_time
 :v_result_limit

 If :v_location_id is NULL, all case locations are considered.
 If :v_vehicle_id is NULL, all case vehicles are considered.
*/
SELECT *
FROM (
    SELECT
        vs.sighting_id,
        vs.vehicle_id,
        ev.entity_id,
        vs.location_id,
        vs.observed_at,
        vs.confidence_score,
        vs.source_reference,
        vs.attributes,
        ev.relationship_type
    FROM VEHICLE_SIGHTINGS vs
    JOIN CASE_VEHICLES cv
      ON cv.case_id = :v_case_id
     AND cv.vehicle_id = vs.vehicle_id
    LEFT JOIN ENTITY_VEHICLES ev
      ON ev.vehicle_id = vs.vehicle_id
     AND (ev.valid_from IS NULL OR vs.observed_at >= ev.valid_from)
     AND (ev.valid_to IS NULL OR vs.observed_at <= ev.valid_to)
    WHERE (:v_location_id IS NULL OR vs.location_id = :v_location_id)
      AND (:v_vehicle_id IS NULL OR vs.vehicle_id = :v_vehicle_id)
      AND vs.observed_at >= :v_start_time
      AND vs.observed_at <= :v_end_time
    ORDER BY vs.observed_at DESC, vs.sighting_id
)
WHERE ROWNUM <= :v_result_limit;
