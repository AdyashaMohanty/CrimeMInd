from __future__ import annotations
import argparse,re
from pathlib import Path
import oracledb
from app.core.config import get_settings
from app.services.auth import register as register_service
from app.models import RegisterRequest

def connect():
    s=get_settings()
    if s.oracle_client_lib_dir:oracledb.init_oracle_client(lib_dir=s.oracle_client_lib_dir)
    return oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.database_url)

def execute_sql_file(conn,path):
    text=path.read_text(encoding="utf-8")
    blocks=[b.strip() for b in re.split(r"(?m)^/\\s*$",text) if b.strip()]
    for block in blocks:
        if block.upper().startswith(("CREATE OR REPLACE FUNCTION","CREATE OR REPLACE TRIGGER")):
            conn.cursor().execute(block)
        else:
            for stmt in block.split(";"):
                stmt=stmt.strip()
                if stmt:conn.cursor().execute(stmt)

def init_db(schema_dir,seed_file=None):
    root=Path(schema_dir)
    ordered=[root/"00_extensions.sql",root/"01_schema.sql",root/"02_sequences.sql",root/"03_indexes.sql",root/"05_seed_reference.sql",root/"06_backend_application.sql",root/"07_case_security.sql"]
    f=root.parent/"functions"
    ordered += [f/"01_evidence_reliability.sql",f/"02_relationship_strength.sql",f/"03_audit_trigger.sql",f/"04_timeline_gaps.sql"]
    if seed_file:ordered.append(Path(seed_file))
    conn=connect()
    try:
        for path in ordered:
            if path.exists():print(f"APPLY {path}");execute_sql_file(conn,path)
        conn.commit()
    finally:conn.close()
    print("Oracle database initialization completed.")

def create_admin(args):
    p=RegisterRequest(full_name=args.name,officer_id=args.officer_id,email=args.email,department=args.department,designation=args.designation,password=args.password,confirm_password=args.password,authorized=True)
    conn=connect()
    try:print(f"Created investigator: {register_service(conn,p)['officer_id']}")
    finally:conn.close()

def main():
    parser=argparse.ArgumentParser(description="CrimeMind Oracle backend administration")
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("init-db");p.add_argument("--schema-dir",default="../database/ddl");p.add_argument("--seed-file");p.set_defaults(fn=lambda a:init_db(a.schema_dir,a.seed_file))
    p=sub.add_parser("create-investigator");p.add_argument("--name",required=True);p.add_argument("--officer-id");p.add_argument("--email",required=True);p.add_argument("--department",required=True);p.add_argument("--designation",default="Investigating Officer");p.add_argument("--password",required=True);p.set_defaults(fn=create_admin)
    a=parser.parse_args();a.fn(a)
if __name__=="__main__":main()
