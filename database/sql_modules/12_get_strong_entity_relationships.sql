/*
 M12 - Strong direct relationships
 Q21: Which entities have the strongest direct relationships with a specified entity?

 Binds:
 :v_case_id
 :v_entity_id
 :v_minimum_strength
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
    WHERE (er.source_entity_id = :v_entity_id
           OR er.target_entity_id = :v_entity_id)
      AND NVL(er.strength_score, 0) >= NVL(:v_minimum_strength, 0)
    ORDER BY er.strength_score DESC NULLS LAST,
             er.relationship_id
)
WHERE ROWNUM <= :v_result_limit;
