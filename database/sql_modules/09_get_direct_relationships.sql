/*
 M09 - Direct relationships
 Q17: What direct relationships does a specified entity have with other entities?

 Binds:
 :v_case_id
 :v_entity_id
 :v_result_limit
*/

SELECT *
FROM (
    SELECT
        er.relationship_id,
        er.relationship_type_id,
        er.source_entity_id,
        er.target_entity_id,
        er.strength_score,
        er.valid_from,
        er.valid_to,
        er.attributes
    FROM ENTITY_RELATIONSHIPS er
    JOIN CASE_ENTITIES cs
      ON cs.case_id = :v_case_id
     AND cs.entity_id = er.source_entity_id
    JOIN CASE_ENTITIES ct
      ON ct.case_id = :v_case_id
     AND ct.entity_id = er.target_entity_id
    WHERE er.source_entity_id = :v_entity_id
       OR er.target_entity_id = :v_entity_id
    ORDER BY er.strength_score DESC NULLS LAST,
             er.relationship_id
)
WHERE ROWNUM <= :v_result_limit;
