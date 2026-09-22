/*
 M13 - Entity vehicles
 Q22: Which vehicles are associated with a specified entity?

 Binds:
 :v_case_id
 :v_entity_id
 :v_result_limit

 Uses only columns confirmed from the supplied ENTITY_VEHICLES schema.
*/

SELECT *
FROM (
    SELECT
        ev.entity_vehicle_id,
        ev.entity_id,
        ev.vehicle_id,
        ev.relationship_type,
        ev.valid_from,
        ev.valid_to
    FROM ENTITY_VEHICLES ev
    JOIN CASE_ENTITIES ce
      ON ce.case_id = :v_case_id
     AND ce.entity_id = ev.entity_id
    WHERE ev.entity_id = :v_entity_id
    ORDER BY ev.vehicle_id
)
WHERE ROWNUM <= :v_result_limit;
