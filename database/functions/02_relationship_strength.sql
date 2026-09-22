CREATE OR REPLACE FUNCTION get_relationship_strength(p_relationship_id NUMBER)
RETURN NUMBER IS v_score NUMBER;
BEGIN
 SELECT NVL(strength_score,0) INTO v_score FROM entity_relationships WHERE relationship_id=p_relationship_id;
 RETURN ROUND(LEAST(GREATEST(v_score,0),1),4);
EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0;
END;
/
