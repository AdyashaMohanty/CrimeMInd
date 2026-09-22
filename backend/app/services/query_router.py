from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from pathlib import Path
from app.core.config import get_settings
from app.db.sql import fetch_one
@dataclass
class Route:code:str;module:str;sql_file:str
QUESTION_TO_MODULE={1:1,2:2,3:1,4:1,5:3,6:5,7:5,8:3,9:4,10:4,11:6,12:6,13:7,14:8,15:8,16:8,17:9,18:10,19:11,20:11,21:12,22:13,23:14,24:14,25:14,26:15,27:15,28:15,29:15,30:15,31:16,32:16,33:17,34:18,35:18,36:17,37:17,38:18,39:18,40:18}
NAMES={1:"01_get_recent_contacts.sql",2:"02_get_communication_between_entities.sql",3:"03_find_entities_near_location.sql",4:"04_find_common_locations.sql",5:"05_get_entity_location_history.sql",6:"06_get_entity_timeline.sql",7:"07_find_timeline_gaps.sql",8:"08_get_events_around_incident.sql",9:"09_get_direct_relationships.sql",10:"10_get_relationship_between_entities.sql",11:"11_find_indirect_connections.sql",12:"12_get_strong_entity_relationships.sql",13:"13_get_entity_vehicles.sql",14:"14_find_vehicles_near_location.sql",15:"15_get_entity_transactions.sql",16:"16_get_entity_evidence.sql",17:"17_find_cross_entity_evidence.sql",18:"18_get_case_evidence_ranking.sql"}
ROUTES={n:Route(f"Q{n}",f"M{m}",NAMES[m]) for n,m in QUESTION_TO_MODULE.items()}
PATTERNS=[(9,r"common locations|locations.*between"),(2,r"communication|communicat|calls?.*between|messages?.*between"),(1,r"recent contacts|who.*contact|contacts.*between|contacted"),(5,r"near.*location|entities.*location|who.*at"),(6,r"location history|locations.*entity|where.*entity"),(11,r"timeline|chronological events|events.*entity"),(13,r"timeline gaps|gaps.*timeline|missing time")]
def route_question(q,p):
    if p.get("question_code"):
        n=int(str(p["question_code"]).upper().replace("Q",""));return (n,ROUTES[n]) if n in ROUTES else (_ for _ in ()).throw(ValueError("Unsupported question code"))
    for n,x in PATTERNS:
        if re.search(x,q,re.I):return n,ROUTES[n]
    raise ValueError("Could not map the question to a supported SQL investigation module. Provide question_code (Q1-Q40).")
def extract_entities(q):return re.findall(r"\bP\d{3,}\b",q.upper())
def extract_locations(q):return re.findall(r"\bL\d{3,}\b",q.upper())
def build_parameters(q,p,case):
    p=dict(p);e=extract_entities(q);l=extract_locations(q);incident=case.get("incident_time") or datetime.now(timezone.utc)
    if incident.tzinfo is None:incident=incident.replace(tzinfo=timezone.utc)
    p.setdefault("start_time",incident-timedelta(hours=24));p.setdefault("end_time",incident+timedelta(hours=24));p.setdefault("result_limit",100)
    if "entity_id" not in p and e:p["entity_id"]=e[0]
    if "entity_a" not in p and e:p["entity_a"]=e[0]
    if "entity_b" not in p and len(e)>1:p["entity_b"]=e[1]
    if "entity_ids" not in p and e:p["entity_ids"]=e
    if "location_id" not in p and l:p["location_id"]=l[0]
    p.setdefault("minimum_entities",max(2,len(e)));p.setdefault("minimum_gap_seconds",1800);p.setdefault("minimum_independent_sources",2);p.setdefault("minimum_reliability",0);p.setdefault("max_hops",3);p.setdefault("window_before",86400);p.setdefault("window_after",86400)
    return p
def resolve_external_ids(conn,p):
    p=dict(p)
    for k in ("entity_id","entity_a","entity_b","start_entity_id","target_entity_id"):
        v=p.get(k)
        if isinstance(v,str) and v.upper().startswith("P"):
            r=fetch_one(conn,"SELECT entity_id FROM entities WHERE external_reference=:ref",{"ref":v.upper()})
            if not r:raise ValueError(f"Unknown entity reference: {v}")
            p[k]=r["entity_id"]
    if isinstance(p.get("entity_ids"),list):
        ids=[]
        for v in p["entity_ids"]:
            if isinstance(v,int):ids.append(v)
            else:
                r=fetch_one(conn,"SELECT entity_id FROM entities WHERE external_reference=:ref",{"ref":str(v).upper()})
                if r:ids.append(r["entity_id"])
        p["entity_ids"]=ids
    v=p.get("location_id")
    if isinstance(v,str) and v.upper().startswith("L"):
        r=fetch_one(conn,"SELECT location_id FROM locations WHERE external_reference=:ref",{"ref":v.upper()})
        if not r:raise ValueError(f"Unknown location reference: {v}")
        p["location_id"]=r["location_id"]
    return p
def load_sql(route):
    for base in [Path(get_settings().sql_module_dir),Path(__file__).resolve().parents[2]/"sql"/"modules",Path.cwd()/Path(get_settings().sql_module_dir)]:
        p=base/route.sql_file
        if p.exists():return p.read_text(encoding="utf-8")
    raise FileNotFoundError(f"SQL module not found: {route.sql_file}")
