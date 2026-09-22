from __future__ import annotations
import json,re
from app.db.sql import fetch_all,execute
from app.services.query_router import route_question,build_parameters,resolve_external_ids,load_sql
def run_query(conn,case,investigator_id,question,mode,provided):
    if mode=="SQL Mode":return run_sql_mode(conn,case,investigator_id,question,provided)
    q,route=route_question(question,provided);params=resolve_external_ids(conn,build_parameters(question,provided,case));sql=load_sql(route)
    try:
        rows=fetch_all(conn,sql,params);_audit(conn,case["case_id"],investigator_id,question,mode,f"Q{q}",route.module,params,sql,len(rows),1,None)
        return {"status":"Query completed","query":{"question":question,"mode":mode,"code":f"Q{q}","module":route.module,"status":"Executed","sql":sql,"parameters":params,"rows":rows},"synthesis":deterministic_synthesis(f"Q{q}",rows)}
    except Exception as exc:_audit(conn,case["case_id"],investigator_id,question,mode,f"Q{q}",route.module,params,sql,0,0,str(exc));raise
def run_sql_mode(conn,case,investigator_id,question,provided):
    sql=question.strip();u=sql.upper();forbidden=["INSERT","UPDATE","DELETE","DROP","ALTER","TRUNCATE","CREATE","GRANT","REVOKE","COPY","CALL","BEGIN","DECLARE","EXECUTE"]
    if not u.startswith("SELECT"):raise ValueError("SQL Mode accepts SELECT statements only.")
    if ";" in sql[:-1]:raise ValueError("Multiple SQL statements are not allowed.")
    if any(re.search(rf"\b{x}\b",u) for x in forbidden):raise ValueError("Only read-only SELECT queries are allowed.")
    try:
        rows=fetch_all(conn,sql,provided);_audit(conn,case["case_id"],investigator_id,question,"SQL Mode",None,"CUSTOM_SELECT",provided,sql,len(rows),1,None)
        return {"status":"Query completed","query":{"question":question,"mode":"SQL Mode","code":None,"module":"CUSTOM_SELECT","status":"Executed","sql":sql,"parameters":provided,"rows":rows},"synthesis":deterministic_synthesis("CUSTOM",rows)}
    except Exception as exc:_audit(conn,case["case_id"],investigator_id,question,"SQL Mode",None,"CUSTOM_SELECT",provided,sql,0,0,str(exc));raise
def deterministic_synthesis(code,rows):
    return {"text":f"Deterministic result for {code}: {len(rows)} record(s) returned. Review the cited records before drawing an investigative conclusion.","explanation":"The backend reports database results only; investigative conclusions remain with the investigator.","citations":[],"confidence":0.70 if rows else 0.0,"advisory":True}
def _audit(conn,case_id,investigator_id,question,mode,query_code,module,params,sql,row_count,success,error):
    execute(conn,"INSERT INTO query_audit(query_audit_id,case_id,investigator_id,question,mode,query_code,module_name,parameters,executed_sql,row_count,success,error_message) VALUES(seq_query_audit.NEXTVAL,:c,:i,:q,:m,:qc,:mod,:p,:sql,:rc,:s,:e)",
            {"c":case_id,"i":investigator_id,"q":question,"m":mode,"qc":query_code,"mod":module,"p":json.dumps(params,default=str),"sql":sql,"rc":row_count,"s":success,"e":error});conn.commit()
