-- Q17
SELECT * FROM (SELECT r.relationship_id,rt.type_name relationship_type,
CASE WHEN r.source_entity_id=:entity_id THEN r.target_entity_id ELSE r.source_entity_id END related_entity_id,
en.display_name related_entity_name,r.strength_score,r.valid_from,r.valid_to,r.attributes
FROM entity_relationships r JOIN relationship_types rt ON rt.relationship_type_id=r.relationship_type_id
JOIN entities en ON en.entity_id=CASE WHEN r.source_entity_id=:entity_id THEN r.target_entity_id ELSE r.source_entity_id END
WHERE r.source_entity_id=:entity_id OR r.target_entity_id=:entity_id ORDER BY r.strength_score DESC NULLS LAST) WHERE ROWNUM<=:result_limit
