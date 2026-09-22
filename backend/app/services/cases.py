import json
from app.db.sql import fetch_all,fetch_one,execute
def get_case(conn,ref):return fetch_one(conn,"SELECT case_id,case_reference,title,opened_at,incident_time,incident_location_id,status,metadata FROM investigation_cases WHERE case_reference=:ref",{"ref":ref})
def list_cases(conn):return fetch_all(conn,"SELECT case_reference,title,status,opened_at,incident_time FROM investigation_cases ORDER BY opened_at DESC,case_reference")
def create_case(conn,payload):
    cid=fetch_one(conn,"SELECT seq_investigation_cases.NEXTVAL id FROM dual")["id"]
    execute(conn,"INSERT INTO investigation_cases(case_id,case_reference,title,status,incident_time,incident_location_id,metadata) VALUES(:id,:case_reference,:title,:status,:incident_time,:incident_location_id,:metadata)",
            {**payload,"id":cid,"metadata":json.dumps(payload.get("metadata",{}))});conn.commit()
    return fetch_one(conn,"SELECT case_id,case_reference,title,status,opened_at,incident_time FROM investigation_cases WHERE case_id=:id",{"id":cid})
def investigator_can_access(conn,investigator_id,case_id):return bool(fetch_one(conn,"SELECT 1 FROM case_investigators WHERE investigator_id=:i AND case_id=:c",{"i":investigator_id,"c":case_id}))
def ensure_case_access(conn,investigator_id,case_id):
    if not investigator_can_access(conn,investigator_id,case_id):
        execute(conn,"INSERT INTO case_investigators(case_id,investigator_id,role) SELECT :c,:i,'INVESTIGATOR' FROM dual WHERE NOT EXISTS(SELECT 1 FROM case_investigators WHERE case_id=:c2 AND investigator_id=:i2)",
                {"c":case_id,"i":investigator_id,"c2":case_id,"i2":investigator_id});conn.commit()
def backfill_case_scope(conn,case_id):
    for table,col in [("case_entities","entity_id"),("case_locations","location_id"),("case_events","event_id"),("case_evidence","evidence_id"),("case_communications","communication_id"),("case_transactions","transaction_id"),("case_vehicles","vehicle_id")]:
        base=table[5:]
        execute(conn,f"INSERT INTO {table}(case_id,{col}) SELECT :c,{col} FROM {base} e WHERE NOT EXISTS(SELECT 1 FROM {table} x WHERE x.case_id=:c2 AND x.{col}=e.{col})",{"c":case_id,"c2":case_id})
    conn.commit()
