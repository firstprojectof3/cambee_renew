# app/routers/crawl_debug.py
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.crawler.sites.ewha_notice import fetch_notice_list, fetch_notice_detail

router = APIRouter()

class PreviewReq(BaseModel):
    list_url: HttpUrl
    take: Optional[int] = 5
    detail_index: Optional[int] = 0  # 목록 중 몇 번째를 상세로 볼지

@router.post("/crawl/preview")
def crawl_preview(req: PreviewReq):
    items = fetch_notice_list(str(req.list_url))[: (req.take or 5)]
    sample_detail = {}
    if items:
        idx = min(max(req.detail_index or 0, 0), len(items)-1)
        sample_detail = fetch_notice_detail(items[idx]["link"])
        # 본문은 너무 길면 미리보기로 컷
        if "body" in sample_detail:
            sample_detail["body"] = sample_detail["body"][:2000]
    return {
        "count": len(items),
        "items": items,
        "sample_detail": sample_detail
    }
