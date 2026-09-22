-- Q18
SELECT * FROM (SELECT r.relationship_id,rt.type_name relationship_type,r.source_entity_id,r.target_entity_id,r.strength_score,r.valid_from,r.valid_to,r.attributes
FROM entity_relationships r JOIN relationship_types rt ON rt.relationship_type_id=r.relationship_type_id
WHERE (r.source_entity_id=:entity_a AND r.target_entity_id=:entity_b) OR (r.source_entity_id=:entity_b AND r.target_entity_id=:entity_a)
ORDER BY r.strength_score DESC NULLS LAST) WHERE ROWNUM<=:result_limit
