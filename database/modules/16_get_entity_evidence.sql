-- Q31,Q32
SELECT * FROM (SELECT ev.evidence_id,et.type_name evidence_type,get_evidence_reliability(ev.evidence_id) reliability,ev.base_confidence,ev.collected_at,ev.source_reference,ev.description,ev.attributes,
CASE WHEN ee.evidence_id IS NOT NULL THEN 'ENTITY' WHEN ex.evidence_id IS NOT NULL THEN 'EVENT' ELSE 'UNLINKED' END association_kind
FROM evidence ev JOIN evidence_types et ON et.evidence_type_id=ev.evidence_type_id
LEFT JOIN evidence_entities ee ON ee.evidence_id=ev.evidence_id AND ee.entity_id=:entity_id LEFT JOIN evidence_events ex ON ex.evidence_id=ev.evidence_id
WHERE (ee.evidence_id IS NOT NULL OR (:event_id IS NOT NULL AND ex.event_id=:event_id)) AND get_evidence_reliability(ev.evidence_id)>=NVL(:minimum_reliability,0)
ORDER BY reliability DESC,ev.collected_at DESC NULLS LAST) WHERE ROWNUM<=:result_limit
