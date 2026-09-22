-- Q34,Q35,Q38,Q39,Q40
WITH candidate_entities AS(SELECT DISTINCT ee.entity_id FROM evidence_entities ee),
evidence_stats AS(SELECT ee.entity_id,COUNT(DISTINCT ev.evidence_id) evidence_volume,COUNT(DISTINCT et.type_name) independent_evidence_types,
SUM(get_evidence_reliability(ev.evidence_id)) cumulative_reliability,MAX(get_evidence_reliability(ev.evidence_id)) max_reliability,
LISTAGG(et.type_name,',') WITHIN GROUP(ORDER BY et.type_name) evidence_types
FROM evidence_entities ee JOIN evidence ev ON ev.evidence_id=ee.evidence_id JOIN evidence_types et ON et.evidence_type_id=ev.evidence_type_id GROUP BY ee.entity_id),
location_links AS(SELECT DISTINCT ee.entity_id FROM evidence_entities ee JOIN evidence_events ex ON ex.evidence_id=ee.evidence_id JOIN events e ON e.event_id=ex.event_id WHERE e.location_id=:location_id),
target_links AS(SELECT DISTINCT ee.entity_id FROM evidence_entities ee WHERE ee.entity_id=:target_entity_id),
relationship_links AS(SELECT DISTINCT CASE WHEN r.source_entity_id=:target_entity_id THEN r.target_entity_id ELSE r.source_entity_id END entity_id FROM entity_relationships r WHERE r.source_entity_id=:target_entity_id OR r.target_entity_id=:target_entity_id)
SELECT * FROM (SELECT ce.entity_id,en.display_name,NVL(es.evidence_volume,0) evidence_volume,NVL(es.independent_evidence_types,0) independent_evidence_types,
NVL(es.cumulative_reliability,0) cumulative_reliability,NVL(es.max_reliability,0) max_reliability,es.evidence_types,
CASE WHEN ll.entity_id IS NOT NULL THEN 1 ELSE 0 END linked_to_location,CASE WHEN tl.entity_id IS NOT NULL THEN 1 ELSE 0 END linked_to_target,
CASE WHEN rl.entity_id IS NOT NULL THEN 1 ELSE 0 END directly_related_to_target,
(CASE WHEN ll.entity_id IS NOT NULL THEN 1 ELSE 0 END+CASE WHEN tl.entity_id IS NOT NULL THEN 1 ELSE 0 END+CASE WHEN rl.entity_id IS NOT NULL THEN 1 ELSE 0 END) cross_domain_link_count,
CASE WHEN NVL(es.independent_evidence_types,0)>=:minimum_independent_sources THEN 1 ELSE 0 END multi_source_corroborated
FROM candidate_entities ce JOIN entities en ON en.entity_id=ce.entity_id LEFT JOIN evidence_stats es ON es.entity_id=ce.entity_id
LEFT JOIN location_links ll ON ll.entity_id=ce.entity_id LEFT JOIN target_links tl ON tl.entity_id=ce.entity_id LEFT JOIN relationship_links rl ON rl.entity_id=ce.entity_id
ORDER BY multi_source_corroborated DESC,cross_domain_link_count DESC,independent_evidence_types DESC,cumulative_reliability DESC,evidence_volume DESC)
WHERE ROWNUM<=:result_limit
