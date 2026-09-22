from fastapi import APIRouter,Depends,HTTPException,status
from app.api.deps import get_db,get_current_investigator,get_case_context
from app.models import LoginRequest,RegisterRequest,QueryRequest,ReviewRequest,CaseCreate
from app.services.auth import register as register_service,login as login_service
from app.services.cases import list_cases,create_case
from app.services.dashboard import dashboard
from app.services.query_service import run_query
from app.services.relationship_graph import build_relationship_graph
from app.db.sql import fetch_all,fetch_one,execute

router=APIRouter()

@router.get("/health")
def health(conn=Depends(get_db)):
    try:
        row=fetch_one(conn,"SELECT 'XE' database,SYSTIMESTAMP server_time FROM dual")
        return {"status":"ok","database":row["database"],"server_time":row["server_time"]}
    except Exception as exc:raise HTTPException(503,f"Database unavailable: {exc}")

@router.post("/auth/register",status_code=201)
def register(payload:RegisterRequest,conn=Depends(get_db)):
    try:return {"message":"Investigator account created","investigator":register_service(conn,payload)}
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(500,f"Registration failed: {exc}")

@router.post("/auth/login")
def login(payload:LoginRequest,conn=Depends(get_db)):
    try:return login_service(conn,payload.officer_id,payload.password)
    except PermissionError as exc:raise HTTPException(status.HTTP_401_UNAUTHORIZED,str(exc))
    except Exception as exc:raise HTTPException(500,f"Login failed: {exc}")

@router.get("/auth/me")
def me(investigator=Depends(get_current_investigator)):return {"investigator":investigator}

@router.get("/cases")
def cases(investigator=Depends(get_current_investigator),conn=Depends(get_db)):return {"cases":list_cases(conn)}

@router.post("/cases",status_code=201)
def create_case_route(payload:CaseCreate,investigator=Depends(get_current_investigator),conn=Depends(get_db)):
    try:
        row=create_case(conn,payload.model_dump(mode="json"))
        execute(conn,"INSERT INTO case_investigators(case_id,investigator_id,role) SELECT :c,:i,'CASE_OWNER' FROM dual WHERE NOT EXISTS(SELECT 1 FROM case_investigators WHERE case_id=:c2 AND investigator_id=:i2)",
                {"c":row["case_id"],"i":investigator["investigator_id"],"c2":row["case_id"],"i2":investigator["investigator_id"]})
        conn.commit();return row
    except Exception as exc:raise HTTPException(400,f"Could not create case: {exc}")

@router.get("/cases/{case_reference}/dashboard")
def case_dashboard(case=Depends(get_case_context),conn=Depends(get_db)):
    try:return dashboard(conn,case["case_id"])
    except Exception as exc:raise HTTPException(500,f"Dashboard query failed: {exc}")

@router.get("/cases/{case_reference}/relationship-graph")
def relationship_graph(case=Depends(get_case_context),conn=Depends(get_db)):
    try:return build_relationship_graph(conn,case["case_id"])
    except Exception as exc:raise HTTPException(500,f"Relationship graph query failed: {exc}")

@router.post("/cases/{case_reference}/queries/run")
def run_case_query(payload:QueryRequest,case=Depends(get_case_context),investigator=Depends(get_current_investigator),conn=Depends(get_db)):
    try:return run_query(conn,case,investigator["investigator_id"],payload.question,payload.mode,payload.parameters)
    except (ValueError,FileNotFoundError) as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(400,f"Query execution failed: {exc}")

@router.post("/cases/{case_reference}/reviews")
def review(payload:ReviewRequest,case=Depends(get_case_context),investigator=Depends(get_current_investigator),conn=Depends(get_db)):
    entity_external=payload.entity_id
    if entity_external and entity_external.isdigit():
        r=fetch_one(conn,"SELECT external_reference FROM entities WHERE entity_id=:id",{"id":int(entity_external)})
        entity_external=r["external_reference"] if r else entity_external
    rid=fetch_one(conn,"SELECT seq_investigator_reviews.NEXTVAL id FROM dual")["id"]
    execute(conn,"INSERT INTO investigator_reviews(review_id,case_id,investigator_id,action,notes,entity_external_reference,synthesis_id) VALUES(:id,:case,:investigator,:action,:notes,:entity,:synthesis)",
            {"id":rid,"case":case["case_id"],"investigator":investigator["investigator_id"],"action":payload.action,"notes":payload.notes,"entity":entity_external,"synthesis":payload.synthesis_id})
    conn.commit()
    return {"status":"Review submitted","review":fetch_one(conn,"SELECT review_id,created_at,action,notes,entity_external_reference,synthesis_id FROM investigator_reviews WHERE review_id=:id",{"id":rid})}

@router.get("/cases/{case_reference}/evidence/{evidence_id}")
def evidence_detail(evidence_id:int,case=Depends(get_case_context),conn=Depends(get_db)):
    row=fetch_one(conn,"""SELECT e.evidence_id id,et.type_name type,e.description,e.collected_at,e.source_reference,e.base_confidence,et.base_weight,
        ROUND(e.base_confidence*et.base_weight,4) reliability FROM evidence e JOIN evidence_types et ON et.evidence_type_id=e.evidence_type_id
        WHERE e.evidence_id=:id AND EXISTS(SELECT 1 FROM case_evidence ce WHERE ce.case_id=:case_id AND ce.evidence_id=e.evidence_id)""",{"id":evidence_id,"case_id":case["case_id"]})
    if not row:raise HTTPException(404,"Evidence not found")
    return row

@router.get("/cases/{case_reference}/entities")
def entities(case=Depends(get_case_context),conn=Depends(get_db)):
    return {"entities":fetch_all(conn,"""SELECT e.entity_id id,e.external_reference,e.display_name,et.type_name entity_type
        FROM entities e JOIN entity_types et ON et.entity_type_id=e.entity_type_id
        WHERE EXISTS(SELECT 1 FROM case_entities ce WHERE ce.case_id=:case_id AND ce.entity_id=e.entity_id)
        ORDER BY e.external_reference""",{"case_id":case["case_id"]})}
