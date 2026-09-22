-- Q33,Q36,Q37
SELECT * FROM (WITH evidence_rollup AS (
SELECT ev.evidence_id,ev.description,COUNT(DISTINCT ee.entity_id) entity_count,COUNT(DISTINCT et.type_name) independent_evidence_types,
LISTAGG(TO_CHAR(ee.entity_id),',') WITHIN GROUP(ORDER BY ee.entity_id) entity_ids,LISTAGG(et.type_name,',') WITHIN GROUP(ORDER BY et.type_name) evidence_types,
get_evidence_reliability(ev.evidence_id) reliability
FROM evidence ev JOIN evidence_types et ON et.evidence_type_id=ev.evidence_type_id JOIN evidence_entities ee ON ee.evidence_id=ev.evidence_id
WHERE ee.entity_id IN (:entity_ids) GROUP BY ev.evidence_id,ev.description HAVING COUNT(DISTINCT ee.entity_id)>=:minimum_entities)
SELECT evidence_rollup.*,CASE WHEN independent_evidence_types>=:minimum_independent_sources THEN 1 ELSE 0 END multi_source_corroborated
FROM evidence_rollup ORDER BY multi_source_corroborated DESC,independent_evidence_types DESC,reliability DESC) WHERE ROWNUM<=:result_limit
