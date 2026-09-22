from __future__ import annotations
import re
def compile_named_sql(sql,params=None):
    values=dict(params or {})
    for key,value in list(values.items()):
        if isinstance(value,(list,tuple,set)):
            seq=list(value)
            if not seq:
                sql=re.sub(rf":{re.escape(key)}\b","NULL",sql);values.pop(key,None);continue
            binds=[]
            for i,item in enumerate(seq):
                n=f"{key}_{i}";binds.append(f":{n}");values[n]=item
            values.pop(key,None);sql=re.sub(rf":{re.escape(key)}\b",",".join(binds),sql)
    return sql,values
def _row(cur,row):
    return dict(zip([d[0].lower() for d in cur.description],row))
def fetch_all(conn,sql,params=None):
    sql,params=compile_named_sql(sql,params)
    with conn.cursor() as cur:
        cur.execute(sql,params or {})
        return [_row(cur,r) for r in cur.fetchall()] if cur.description else []
def fetch_one(conn,sql,params=None):
    rows=fetch_all(conn,sql,params);return rows[0] if rows else None
def execute(conn,sql,params=None):
    sql,params=compile_named_sql(sql,params)
    with conn.cursor() as cur:cur.execute(sql,params or {});return cur.rowcount
