from datetime import datetime,timezone
import secrets
from app.db.sql import fetch_one,execute
from app.core.security import hash_password,verify_password,create_access_token
def register(conn,payload):
    if payload.password!=payload.confirm_password:raise ValueError("Passwords do not match")
    if not payload.authorized:raise ValueError("Authorization confirmation is required")
    officer_id=payload.officer_id.strip().upper() if payload.officer_id else _generate_officer_id(conn,payload.full_name)
    if fetch_one(conn,"SELECT investigator_id FROM investigators WHERE officer_id=:officer_id OR email=:email",{"officer_id":officer_id,"email":payload.email.strip().lower()}):
        raise ValueError("Officer ID or email already exists")
    iid=fetch_one(conn,"SELECT seq_investigators.NEXTVAL id FROM dual")["id"]
    execute(conn,'''INSERT INTO investigators(investigator_id,officer_id,full_name,email,department,designation,password_hash,is_active,is_authorized)
                    VALUES(:id,:officer_id,:full_name,:email,:department,:designation,:password_hash,1,1)''',
            {"id":iid,"officer_id":officer_id,"full_name":payload.full_name.strip(),"email":payload.email.strip().lower(),
             "department":payload.department.strip(),"designation":payload.designation.strip(),"password_hash":hash_password(payload.password)})
    conn.commit()
    return fetch_one(conn,"SELECT investigator_id,officer_id,full_name,email,department,designation,is_authorized FROM investigators WHERE investigator_id=:id",{"id":iid})
def login(conn,officer_id,password):
    row=fetch_one(conn,'''SELECT investigator_id,officer_id,full_name,email,department,designation,password_hash,is_active,is_authorized
                          FROM investigators WHERE officer_id=:officer_id''',{"officer_id":officer_id.strip().upper()})
    if not row or row["is_active"]!=1 or row["is_authorized"]!=1 or not verify_password(password,row["password_hash"]):raise PermissionError("Invalid Officer ID or password")
    execute(conn,"UPDATE investigators SET last_login_at=:now WHERE investigator_id=:id",{"now":datetime.now(timezone.utc),"id":row["investigator_id"]});conn.commit()
    token=create_access_token(str(row["investigator_id"]),row["officer_id"])
    return {"access_token":token,"token_type":"bearer","investigator":{"id":row["investigator_id"],"officer_id":row["officer_id"],"name":row["full_name"],"email":row["email"],"department":row["department"],"designation":row["designation"]}}
def _generate_officer_id(conn,full_name):
    base="".join(ch for ch in full_name.upper() if ch.isalpha())[:3] or "INS"
    for _ in range(20):
        candidate=f"{base}-{secrets.randbelow(9000)+1000}"
        if not fetch_one(conn,"SELECT investigator_id FROM investigators WHERE officer_id=:id",{"id":candidate}):return candidate
    raise RuntimeError("Could not generate a unique Officer ID")
