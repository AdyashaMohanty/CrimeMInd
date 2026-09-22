from __future__ import annotations
import json, os, sys
from pathlib import Path
import oracledb

DSN=os.getenv("DATABASE_URL","localhost:1521/XE")
USER=os.getenv("ORACLE_USER","CRIMEMIND")
PASSWORD=os.getenv("ORACLE_PASSWORD")
CLIENT=os.getenv("ORACLE_CLIENT_LIB_DIR")

def connect():
    if CLIENT:
        oracledb.init_oracle_client(lib_dir=CLIENT)
    if not PASSWORD:
        raise RuntimeError("Set ORACLE_PASSWORD before loading data.")
    return oracledb.connect(user=USER,password=PASSWORD,dsn=DSN)

def one(cur,sql,**binds):
    cur.execute(sql,binds)
    return cur.fetchone()

def next_id(cur,sequence):
    return one(cur,f"SELECT {sequence}.NEXTVAL FROM dual")[0]

def id_by(cur,table,id_col,name_col,value):
    row=one(cur,f"SELECT {id_col} FROM {table} WHERE {name_col}=:v",v=value)
    if not row:
        raise ValueError(f"{name_col} '{value}' not found in {table}")
    return row[0]

def get_or_create_location(cur,name):
    row=one(cur,"SELECT location_id FROM locations WHERE location_name=:n",n=name)
    if row:return row[0]
    lid=next_id(cur,"seq_locations")
    cur.execute("INSERT INTO locations(location_id,location_name) VALUES(:id,:n)",{"id":lid,"n":name})
    return lid

def load_case(cur,record):
    c=record["case"]
    lid=get_or_create_location(cur,c["incident_location"]) if c.get("incident_location") else None
    row=one(cur,"SELECT case_id FROM investigation_cases WHERE case_reference=:ref",ref=c["case_reference"])
    metadata=json.dumps(c.get("metadata",{}))
    if row:
        cid=row[0]
        cur.execute("""UPDATE investigation_cases
                       SET title=:title,incident_time=:itime,incident_location_id=:lid,status=:status,metadata=:meta
                       WHERE case_id=:id""",
                    {"title":c["title"],"itime":c.get("incident_time"),"lid":lid,
                     "status":c.get("status","OPEN"),"meta":metadata,"id":cid})
    else:
        cid=next_id(cur,"seq_investigation_cases")
        cur.execute("""INSERT INTO investigation_cases
                       (case_id,case_reference,title,incident_time,incident_location_id,status,metadata)
                       VALUES(:id,:ref,:title,:itime,:lid,:status,:meta)""",
                    {"id":cid,"ref":c["case_reference"],"title":c["title"],"itime":c.get("incident_time"),
                     "lid":lid,"status":c.get("status","OPEN"),"meta":metadata})
    return cid

def load_entity(cur,record):
    e=record["entity"]
    type_id=id_by(cur,"entity_types","entity_type_id","type_name",e.get("entity_type","UNKNOWN"))
    row=one(cur,"SELECT entity_id FROM entities WHERE external_reference=:ref",ref=e["external_reference"])
    if row:
        eid=row[0]
        cur.execute("UPDATE entities SET entity_type_id=:tid,display_name=:name WHERE entity_id=:id",
                    {"tid":type_id,"name":e["display_name"],"id":eid})
    else:
        eid=next_id(cur,"seq_entities")
        cur.execute("""INSERT INTO entities(entity_id,entity_type_id,display_name,external_reference)
                       VALUES(:id,:tid,:name,:ref)""",
                    {"id":eid,"tid":type_id,"name":e["display_name"],"ref":e["external_reference"]})
    return eid

def load_evidence(cur,record):
    e=record["evidence"]
    evidence_type=e.get("evidence_type",e.get("type","DOCUMENT"))
    type_id=id_by(cur,"evidence_types","evidence_type_id","type_name",evidence_type)
    eid=next_id(cur,"seq_evidence")
    cur.execute("""INSERT INTO evidence
                   (evidence_id,evidence_type_id,collected_at,source_reference,base_confidence,attributes,description)
                   VALUES(:id,:tid,:at,:src,:conf,:attrs,:desc)""",
                {"id":eid,"tid":type_id,"at":e.get("collected_at"),"src":record.get("source_file"),
                 "conf":e.get("base_confidence",0.5),"attrs":json.dumps(e.get("attributes",{})),
                 "desc":e.get("description")})
    refs=e.get("entity_references",[])
    if isinstance(refs,str):refs=[refs]
    for ref in refs:
        row=one(cur,"SELECT entity_id FROM entities WHERE external_reference=:ref",ref=ref)
        if row:
            link=next_id(cur,"seq_evidence_entities")
            cur.execute("""INSERT INTO evidence_entities
                           (evidence_entity_id,evidence_id,entity_id,association_confidence,relation_role)
                           VALUES(:lid,:eid,:ent,:conf,:role)""",
                        {"lid":link,"eid":eid,"ent":row[0],"conf":e.get("association_confidence",1.0),
                         "role":e.get("relation_role","SUBJECT")})
    return eid

def backfill(cur,case_id):
    for table,col,base in [
        ("case_entities","entity_id","entities"),("case_locations","location_id","locations"),
        ("case_events","event_id","events"),("case_evidence","evidence_id","evidence"),
        ("case_communications","communication_id","communications"),
        ("case_transactions","transaction_id","transactions"),("case_vehicles","vehicle_id","vehicles")]:
        cur.execute(f"""INSERT INTO {table}(case_id,{col})
                        SELECT :cid,{col} FROM {base} e
                        WHERE NOT EXISTS(SELECT 1 FROM {table} x WHERE x.case_id=:c AND x.{col}=e.{col})""",
                    {"cid":case_id,"c":case_id})

def main(input_path):
    data=json.loads(Path(input_path).read_text(encoding="utf-8"))
    conn=connect()
    counts={"cases":0,"entities":0,"evidence":0}
    case_ids=set()
    try:
        cur=conn.cursor()
        for record in data["records"]:
            if "case" in record:
                case_ids.add(load_case(cur,record));counts["cases"]+=1
            elif "entity" in record:
                load_entity(cur,record);counts["entities"]+=1
            elif "evidence" in record:
                load_evidence(cur,record);counts["evidence"]+=1
        for cid in case_ids:backfill(cur,cid)
        conn.commit()
        links=one(cur,"SELECT COUNT(*) FROM evidence_entities")[0]
        print("="*40)
        print("ORACLE LOAD SUMMARY")
        print("="*40)
        print(f"Cases loaded        : {counts['cases']}")
        print(f"Entities loaded     : {counts['entities']}")
        print(f"Evidence loaded     : {counts['evidence']}")
        print(f"Evidence links      : {links}")
        print(f"Input records       : {len(data['records'])}")
        print("="*40)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m ingestion.loaders.oracle_loader <normalized_json>")
    main(Path(sys.argv[1]))
