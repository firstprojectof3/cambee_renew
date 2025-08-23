# app/repo/notice_repo.py
from __future__ import annotations
from typing import Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session

def bulk_insert_raw(db: Session, rows: List[Dict]):
    if not rows:
        return 0
    sql = text("""
        INSERT INTO app.notice_raw (url, status, html, error)
        VALUES (:url, :status, :html, :error)
    """)
    for r in rows:
        db.execute(sql, {
            "url": r.get("url"),
            "status": r.get("status", "ok"),
            "html": r.get("html"),
            "error": r.get("error")
        })
    return len(rows)

def upsert_notice(db: Session, n: Dict):
    """
    n = {
      url, url_key, title, body, category, posted_at(YYYY-MM-DD|None), checksum
    }
    """
    sql = text("""
        INSERT INTO app.notice
            (url, url_key, title, body, category, posted_at, checksum)
        VALUES
            (:url, :url_key, :title, :body, :category, :posted_at, :checksum)
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            body = EXCLUDED.body,
            category = COALESCE(EXCLUDED.category, app.notice.category),
            posted_at = COALESCE(EXCLUDED.posted_at, app.notice.posted_at),
            checksum = EXCLUDED.checksum,
            updated_at = NOW()
        RETURNING
            (xmax = 0) AS inserted;  -- Postgres trick: true면 새로 insert
    """)
    res = db.execute(sql, {
        "url": n["url"],
        "url_key": n["url_key"],
        "title": n["title"],
        "body": n["body"],
        "category": n.get("category"),
        "posted_at": n.get("posted_at"),
        "checksum": n.get("checksum")
    }).first()
    # inserted=True면 신규, False면 업데이트/스킵
    return bool(res.inserted) if res and hasattr(res, "inserted") else False
