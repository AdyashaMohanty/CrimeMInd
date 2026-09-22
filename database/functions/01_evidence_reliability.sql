CREATE OR REPLACE FUNCTION get_evidence_reliability(p_evidence_id NUMBER)
RETURN NUMBER
IS v_base NUMBER; v_conf NUMBER; v_assoc NUMBER; v_score NUMBER;
BEGIN
 SELECT et.base_weight,e.base_confidence INTO v_base,v_conf
 FROM evidence e JOIN evidence_types et ON et.evidence_type_id=e.evidence_type_id
 WHERE e.evidence_id=p_evidence_id;
 SELECT NVL(AVG(association_confidence),1) INTO v_assoc FROM evidence_entities WHERE evidence_id=p_evidence_id;
 v_score:=NVL(v_base,0)*NVL(v_conf,0)*NVL(v_assoc,1);
 RETURN ROUND(LEAST(GREATEST(v_score,0),1),4);
EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0;
END;
/
