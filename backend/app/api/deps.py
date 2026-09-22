from collections.abc import Generator
from fastapi import Depends,HTTPException,status
from app.core.security import oauth2_scheme,decode_access_token
from app.db.pool import db_conn
from app.db.sql import fetch_one,execute
from app.services.cases import ensure_case_access
def get_db()->Generator:
    with db_conn() as conn:yield conn
def get_current_investigator(token:str=Depends(oauth2_scheme),conn=Depends(get_db)):
    p=decode_access_token(token)
    try:iid=int(p.get("sub"))
    except (TypeError,ValueError):raise HTTPException(401,"Invalid token subject")
    row=fetch_one(conn,"SELECT investigator_id,officer_id,full_name,email,department,designation,is_active,is_authorized FROM investigators WHERE investigator_id=:id",{"id":iid})
    if not row or row["is_active"]!=1 or row["is_authorized"]!=1:raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Investigator account is inactive or unauthorized")
    return row
def get_case_context(case_reference:str,investigator=Depends(get_current_investigator),conn=Depends(get_db)):
    row=fetch_one(conn,"SELECT case_id,case_reference,title,status,opened_at,incident_time,incident_location_id,metadata FROM investigation_cases WHERE case_reference=:ref",{"ref":case_reference})
    if not row:raise HTTPException(404,"Case not found")
    ensure_case_access(conn,investigator["investigator_id"],row["case_id"])
    execute(conn,"BEGIN crimemind_security_ctx.set_case(:case_id); END;",{"case_id":row["case_id"]})
    return row
