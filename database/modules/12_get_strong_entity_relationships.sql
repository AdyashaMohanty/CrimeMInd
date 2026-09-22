-- Q21
SELECT * FROM (SELECT r.relationship_id,rt.type_name relationship_type,
CASE WHEN r.source_entity_id=:entity_id THEN r.target_entity_id ELSE r.source_entity_id END related_entity_id,en.display_name related_entity_name,
get_relationship_strength(r.relationship_id) strength_score
FROM entity_relationships r JOIN relationship_types rt ON rt.relationship_type_id=r.relationship_type_id
JOIN entities en ON en.entity_id=CASE WHEN r.source_entity_id=:entity_id THEN r.target_entity_id ELSE r.source_entity_id END
WHERE (r.source_entity_id=:entity_id OR r.target_entity_id=:entity_id) AND get_relationship_strength(r.relationship_id)>=:minimum_strength
ORDER BY strength_score DESC) WHERE ROWNUM<=:result_limit
