from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CrimeMind API"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = "localhost:1521/XE"
    oracle_user: str = "CRIMEMIND"
    oracle_password: str
    oracle_client_lib_dir: str | None = None
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    sql_module_dir: str = "../database/modules"
    default_result_limit: int = 100
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    @property
    def cors_origin_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def get_settings(): return Settings()
