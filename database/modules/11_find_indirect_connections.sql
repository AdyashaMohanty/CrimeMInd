-- Q19,Q20
SELECT * FROM (SELECT target_entity_id,MIN(LEVEL) shortest_hops,
MIN(SYS_CONNECT_BY_PATH(TO_CHAR(source_entity_id),' -> ')||' -> '||TO_CHAR(target_entity_id)) example_path,
MIN(SYS_CONNECT_BY_PATH(TO_CHAR(relationship_id),' -> ')) example_relationship_path
FROM entity_relationships START WITH source_entity_id=:start_entity_id
CONNECT BY NOCYCLE PRIOR target_entity_id=source_entity_id AND LEVEL<:max_hops
GROUP BY target_entity_id HAVING target_entity_id=:target_entity_id ORDER BY shortest_hops) WHERE ROWNUM<=:result_limit
