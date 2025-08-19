# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session, declarative_base

DB_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="cambee_admin",
    password="Cambee2025!",  # 비밀번호
    host="cambee-db.c10wgg8su66w.ap-northeast-2.rds.amazonaws.com",
    port=5432,
    database="postgres",      # ⬅️ 여기 꼭 바꾸기!
    query={"sslmode": "require"},  # ⬅️ RDS는 SSL 권장
)

engine = create_engine(DB_URL, pool_pre_ping=True)  # ⬅️ 헬스체크
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
