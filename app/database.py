# app/database.py
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from app.core import config
from app.core.config import SETTINGS



def _ensure_sslmode(url: str) -> str:
    """
    RDS 등 외부 DB 사용 시 sslmode=require가 없으면 자동으로 붙여준다.
    (postgres 스킴일 때만 동작)
    """
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme.startswith("postgresql"):
        return url

    query = dict(parse_qsl(parsed.query)) if parsed.query else {}
    if "sslmode" not in query:
        query["sslmode"] = "require"

    new_query = urlencode(query)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )


# 1) .env에서 로드된 DATABASE_URL을 사용 (config.py에서 이미 load_dotenv 완료)
#    예시) postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME
DB_URL = _ensure_sslmode(SETTINGS.database_url)

if not DB_URL:
    raise RuntimeError(
        "[DATABASE] DATABASE_URL이 비어있습니다. .env에 DATABASE_URL을 설정하세요.\n"
        "예) DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname"
    )

# 2) 엔진 & 세션팩토리
# - pool_pre_ping=True: 연결 헬스체크로 stale connection 방지
# - pool_recycle=1800: 30분마다 커넥션 재활용(일부 클라우드 환경 타임아웃 대응)
engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3) Base & 의존성
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
