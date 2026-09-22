CREATE OR REPLACE TRIGGER trg_audit_events
AFTER INSERT OR UPDATE OR DELETE ON events FOR EACH ROW
BEGIN
 INSERT INTO audit_log(audit_id,table_name,operation,row_pk,changed_at,changed_by,old_data,new_data)
 VALUES(seq_audit_log.NEXTVAL,'EVENTS',
 CASE WHEN INSERTING THEN 'INSERT' WHEN UPDATING THEN 'UPDATE' ELSE 'DELETE' END,
 TO_CHAR(NVL(:NEW.event_id,:OLD.event_id)),SYSTIMESTAMP,USER,
 CASE WHEN INSERTING THEN NULL ELSE '{"event_id":'||TO_CHAR(:OLD.event_id)||'}' END,
 CASE WHEN DELETING THEN NULL ELSE '{"event_id":'||TO_CHAR(:NEW.event_id)||'}' END);
END;
/
CREATE OR REPLACE TRIGGER trg_audit_evidence
AFTER INSERT OR UPDATE OR DELETE ON evidence FOR EACH ROW
BEGIN
 INSERT INTO audit_log(audit_id,table_name,operation,row_pk,changed_at,changed_by,old_data,new_data)
 VALUES(seq_audit_log.NEXTVAL,'EVIDENCE',
 CASE WHEN INSERTING THEN 'INSERT' WHEN UPDATING THEN 'UPDATE' ELSE 'DELETE' END,
 TO_CHAR(NVL(:NEW.evidence_id,:OLD.evidence_id)),SYSTIMESTAMP,USER,
 CASE WHEN INSERTING THEN NULL ELSE '{"evidence_id":'||TO_CHAR(:OLD.evidence_id)||'}' END,
 CASE WHEN DELETING THEN NULL ELSE '{"evidence_id":'||TO_CHAR(:NEW.evidence_id)||'}' END);
END;
/
CREATE OR REPLACE TRIGGER trg_audit_transactions
AFTER INSERT OR UPDATE OR DELETE ON transactions FOR EACH ROW
BEGIN
 INSERT INTO audit_log(audit_id,table_name,operation,row_pk,changed_at,changed_by,old_data,new_data)
 VALUES(seq_audit_log.NEXTVAL,'TRANSACTIONS',
 CASE WHEN INSERTING THEN 'INSERT' WHEN UPDATING THEN 'UPDATE' ELSE 'DELETE' END,
 TO_CHAR(NVL(:NEW.transaction_id,:OLD.transaction_id)),SYSTIMESTAMP,USER,
 CASE WHEN INSERTING THEN NULL ELSE '{"transaction_id":'||TO_CHAR(:OLD.transaction_id)||'}' END,
 CASE WHEN DELETING THEN NULL ELSE '{"transaction_id":'||TO_CHAR(:NEW.transaction_id)||'}' END);
END;
/
CREATE OR REPLACE TRIGGER trg_audit_relationships
AFTER INSERT OR UPDATE OR DELETE ON entity_relationships FOR EACH ROW
BEGIN
 INSERT INTO audit_log(audit_id,table_name,operation,row_pk,changed_at,changed_by,old_data,new_data)
 VALUES(seq_audit_log.NEXTVAL,'ENTITY_RELATIONSHIPS',
 CASE WHEN INSERTING THEN 'INSERT' WHEN UPDATING THEN 'UPDATE' ELSE 'DELETE' END,
 TO_CHAR(NVL(:NEW.relationship_id,:OLD.relationship_id)),SYSTIMESTAMP,USER,
 CASE WHEN INSERTING THEN NULL ELSE '{"relationship_id":'||TO_CHAR(:OLD.relationship_id)||'}' END,
 CASE WHEN DELETING THEN NULL ELSE '{"relationship_id":'||TO_CHAR(:NEW.relationship_id)||'}' END);
END;
/
