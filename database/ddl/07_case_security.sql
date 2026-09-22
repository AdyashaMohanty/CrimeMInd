-- Oracle equivalent of legacy PostgreSQL case RLS using Virtual Private Database (DBMS_RLS).
-- A request sets CRIMEMIND_CTX.CASE_ID. If no case is selected, protected rows are invisible.

CREATE OR REPLACE PACKAGE crimemind_security_ctx AS
  PROCEDURE set_case(p_case_id NUMBER);
  PROCEDURE clear_case;
END;
/
CREATE OR REPLACE PACKAGE BODY crimemind_security_ctx AS
  PROCEDURE set_case(p_case_id NUMBER) IS
  BEGIN
    DBMS_SESSION.SET_CONTEXT('CRIMEMIND_CTX','CASE_ID',TO_CHAR(p_case_id));
  END;
  PROCEDURE clear_case IS
  BEGIN
    DBMS_SESSION.CLEAR_CONTEXT('CRIMEMIND_CTX','CASE_ID');
  END;
END;
/
CREATE CONTEXT crimemind_ctx USING crimemind_security_ctx;

CREATE OR REPLACE FUNCTION crimemind_case_policy(
  p_schema VARCHAR2,p_object VARCHAR2
) RETURN VARCHAR2 IS
  v_case VARCHAR2(100):=SYS_CONTEXT('CRIMEMIND_CTX','CASE_ID');
BEGIN
  IF v_case IS NULL THEN RETURN '1=0'; END IF;
  CASE UPPER(p_object)
    WHEN 'ENTITIES' THEN RETURN 'EXISTS (SELECT 1 FROM case_entities ce WHERE ce.entity_id=entities.entity_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'LOCATIONS' THEN RETURN 'EXISTS (SELECT 1 FROM case_locations cl WHERE cl.location_id=locations.location_id AND cl.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'EVENTS' THEN RETURN 'EXISTS (SELECT 1 FROM case_events ce WHERE ce.event_id=events.event_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'ENTITY_EVENTS' THEN RETURN 'EXISTS (SELECT 1 FROM case_events ce WHERE ce.event_id=entity_events.event_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'ENTITY_RELATIONSHIPS' THEN RETURN 'EXISTS (SELECT 1 FROM case_entities a WHERE a.entity_id=entity_relationships.source_entity_id AND a.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID''))) AND EXISTS (SELECT 1 FROM case_entities b WHERE b.entity_id=entity_relationships.target_entity_id AND b.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'COMMUNICATIONS' THEN RETURN 'EXISTS (SELECT 1 FROM case_communications cc WHERE cc.communication_id=communications.communication_id AND cc.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'VEHICLES' THEN RETURN 'EXISTS (SELECT 1 FROM case_vehicles cv WHERE cv.vehicle_id=vehicles.vehicle_id AND cv.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'ENTITY_VEHICLES' THEN RETURN 'EXISTS (SELECT 1 FROM case_vehicles cv WHERE cv.vehicle_id=entity_vehicles.vehicle_id AND cv.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'VEHICLE_SIGHTINGS' THEN RETURN 'EXISTS (SELECT 1 FROM case_vehicles cv WHERE cv.vehicle_id=vehicle_sightings.vehicle_id AND cv.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'TRANSACTIONS' THEN RETURN 'EXISTS (SELECT 1 FROM case_transactions ct WHERE ct.transaction_id=transactions.transaction_id AND ct.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'EVIDENCE' THEN RETURN 'EXISTS (SELECT 1 FROM case_evidence ce WHERE ce.evidence_id=evidence.evidence_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'EVIDENCE_ENTITIES' THEN RETURN 'EXISTS (SELECT 1 FROM case_evidence ce WHERE ce.evidence_id=evidence_entities.evidence_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    WHEN 'EVIDENCE_EVENTS' THEN RETURN 'EXISTS (SELECT 1 FROM case_evidence ce WHERE ce.evidence_id=evidence_events.evidence_id AND ce.case_id=TO_NUMBER(SYS_CONTEXT(''CRIMEMIND_CTX'',''CASE_ID'')))';
    ELSE RETURN '1=0';
  END CASE;
END;
/
BEGIN
  FOR t IN (SELECT 'ENTITIES' n FROM dual UNION ALL SELECT 'LOCATIONS' FROM dual UNION ALL SELECT 'EVENTS' FROM dual
            UNION ALL SELECT 'ENTITY_EVENTS' FROM dual UNION ALL SELECT 'ENTITY_RELATIONSHIPS' FROM dual
            UNION ALL SELECT 'COMMUNICATIONS' FROM dual UNION ALL SELECT 'VEHICLES' FROM dual UNION ALL SELECT 'ENTITY_VEHICLES' FROM dual
            UNION ALL SELECT 'VEHICLE_SIGHTINGS' FROM dual UNION ALL SELECT 'TRANSACTIONS' FROM dual UNION ALL SELECT 'EVIDENCE' FROM dual
            UNION ALL SELECT 'EVIDENCE_ENTITIES' FROM dual UNION ALL SELECT 'EVIDENCE_EVENTS' FROM dual) LOOP
    BEGIN DBMS_RLS.DROP_POLICY(USER,t.n,'CRIMEMIND_CASE_POLICY'); EXCEPTION WHEN OTHERS THEN NULL; END;
    DBMS_RLS.ADD_POLICY(USER,t.n,'CRIMEMIND_CASE_POLICY','CRIMEMIND_CASE_POLICY','CRIMEMIND_CASE_POLICY',DBMS_RLS.STATIC);
  END LOOP;
END;
/
