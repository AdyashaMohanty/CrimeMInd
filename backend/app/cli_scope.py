from __future__ import annotations
import argparse,oracledb
from app.core.config import get_settings
from app.services.cases import get_case,backfill_case_scope
def main():
    p=argparse.ArgumentParser(description="Backfill CrimeMind case scope")
    p.add_argument("case_reference");a=p.parse_args();s=get_settings()
    if s.oracle_client_lib_dir:oracledb.init_oracle_client(lib_dir=s.oracle_client_lib_dir)
    c=oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.database_url)
    try:
        row=get_case(c,a.case_reference)
        if not row:raise SystemExit(f"Case not found: {a.case_reference}")
        backfill_case_scope(c,row["case_id"])
    finally:c.close()
    print(f"Case scope backfilled for {a.case_reference}")
if __name__=="__main__":main()
