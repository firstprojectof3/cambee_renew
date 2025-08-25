# app/core/config.py
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# .env 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)
else:
    print(f"[WARN] .env not found: {ENV_PATH}")

def _as_list(val: str) -> list[str]:
    return [s.strip() for s in val.split(",") if s.strip()]

def _as_int(key: str, default: int) -> int:
    try: return int(os.getenv(key, str(default)))
    except: return default

def _as_float(key: str, default: float) -> float:
    try: return float(os.getenv(key, str(default)))
    except: return default

@dataclass(frozen=True)
class Settings:
    database_url: str
    openai_api_key: str
    prompt_id: str
    prompt_version: str
    model_general: str
    model_expert: str
    cache_ttl_sec: int
    sim_threshold: float
    cors_origins: list[str]

def load_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        prompt_id=os.getenv("CAMBEE_PROMPT_ID", ""),
        prompt_version=os.getenv("CAMBEE_PROMPT_VERSION", "latest"),
        model_general=os.getenv("MODEL_GENERAL", "gpt-4o-mini"),
        model_expert=os.getenv("MODEL_EXPERT", "gpt-4o"),
        cache_ttl_sec=_as_int("CACHE_TTL_SEC", 86400),
        sim_threshold=_as_float("SIM_THRESHOLD", 0.88),
        cors_origins=_as_list(os.getenv("CORS_ORIGINS", "https://effective-chainsaw-97wv5xvxppqw27xpq-8000.app.github.dev")),
    )

SETTINGS = load_settings()

# 확인 로그(민감값 미노출)
print("🔧 [CONFIG] DB_URL     =", "SET" if SETTINGS.database_url else "NOT SET")
print("🔧 [CONFIG] OPENAI_KEY =", "SET" if SETTINGS.openai_api_key else "NOT SET")
print("🔧 [CONFIG] PROMPT_ID  =", "SET" if SETTINGS.prompt_id else "NOT SET")
print("🔧 [CONFIG] MODELS     =", SETTINGS.model_general, "/", SETTINGS.model_expert)
print("🔧 [CONFIG] CORS       =", SETTINGS.cors_origins)
