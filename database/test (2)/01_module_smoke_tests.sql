-- Oracle smoke tests. Run after database installation and synthetic seed.
SET SERVEROUTPUT ON
DECLARE n NUMBER;
BEGIN
 SELECT COUNT(*) INTO n FROM entity_types; DBMS_OUTPUT.PUT_LINE('entity_types='||n);
 SELECT COUNT(*) INTO n FROM evidence_types; DBMS_OUTPUT.PUT_LINE('evidence_types='||n);
 SELECT COUNT(*) INTO n FROM investigation_queries; DBMS_OUTPUT.PUT_LINE('queries='||n);
 SELECT COUNT(*) INTO n FROM sql_modules; DBMS_OUTPUT.PUT_LINE('modules='||n);
 IF n<>18 THEN RAISE_APPLICATION_ERROR(-20001,'Expected 18 SQL modules'); END IF;
END;
/
