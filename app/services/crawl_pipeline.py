# app/services/crawl_pipeline.py
from __future__ import annotations
from typing import Dict
from sqlalchemy.orm import Session

from app.crawler.sites.ewha_notice import fetch_notice_list, fetch_notice_detail
from app.crawler.utils import make_url_key, body_checksum
from app.repo.notice_repo import upsert_notice, bulk_insert_raw

def crawl_and_store(db: Session, list_url: str, limit: int = 50) -> Dict:
    items = fetch_notice_list(list_url)[:limit]

    inserted = updated = skipped = errors = 0
    raw_logs = []

    for it in items:
        url = it["link"]
        try:
            detail = fetch_notice_detail(url)

            title = detail.get("title") or it.get("title") or ""
            body  = detail.get("body") or ""
            category = it.get("category")
            posted_at = detail.get("posted_at") or it.get("posted_at")
            url_key = make_url_key(url)
            checksum = body_checksum(body, title)

            row = {
                "url": url,
                "url_key": url_key,
                "title": title,
                "body": body,
                "category": category,
                "posted_at": posted_at,
                "checksum": checksum
            }

            inserted_flag = upsert_notice(db, row)
            if inserted_flag:
                inserted += 1
            else:
                # 변경 감지는 upsert에서 처리됐으므로, 여기서는 일단 updated/skip 구분 생략.
                # 필요하면 SELECT로 기존 checksum 비교해 세부 카운트 가능.
                updated += 1  # 실무에선 updated/skip 분리 권장
            raw_logs.append({"url": url, "status": "ok", "html": None, "error": None})

        except Exception as e:
            errors += 1
            raw_logs.append({"url": url, "status": "error", "html": None, "error": str(e)})

    bulk_insert_raw(db, raw_logs)
    db.commit()

    # updated에서 진짜 변경만 카운트하고 싶다면, 별도 SELECT 비교 로직 추가 가능.
    return {"found": len(items), "inserted": inserted, "updated_or_skipped": updated, "errors": errors}
