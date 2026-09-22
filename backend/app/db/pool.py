from contextlib import contextmanager
import oracledb
from app.core.config import get_settings

_initialized=False

def initialize_oracle():
    global _initialized
    if _initialized:return
    s=get_settings()
    if s.oracle_client_lib_dir:oracledb.init_oracle_client(lib_dir=s.oracle_client_lib_dir)
    _initialized=True

class OraclePool:
    def __init__(self):self.pool=None
    def open(self):
        initialize_oracle()
        if self.pool is None:
            s=get_settings()
            self.pool=oracledb.create_pool(user=s.oracle_user,password=s.oracle_password,dsn=s.database_url,
                                           min=1,max=10,increment=1,getmode=oracledb.SPOOL_ATTRVAL_WAIT)
    def close(self):
        if self.pool:
            self.pool.close()
            self.pool=None
    @contextmanager
    def connection(self):
        if self.pool is None:self.open()
        c=self.pool.acquire()
        try:
            yield c
        finally:
            try:
                with c.cursor() as cur:cur.execute("BEGIN crimemind_security_ctx.clear_case; END;")
            except Exception:
                pass
            self.pool.release(c)

pool=OraclePool()

@contextmanager
def db_conn():
    with pool.connection() as conn:yield conn
