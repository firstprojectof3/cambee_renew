# app/crud/notice.py
from sqlalchemy import desc
from app.models.models import Notice

def get_recent_notices(db, limit: int = 30):
    # date가 없을 수도 있으니 보강
    q = db.query(Notice)
    try:
        return q.order_by(desc(Notice.date)).limit(limit).all()
    except Exception:
        # date가 null인 레코드가 섞여 있으면 id 역순으로 폴백
        return q.order_by(desc(Notice.id)).limit(limit).all()
