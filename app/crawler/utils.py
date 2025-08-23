# app/crawler/utils.py
from __future__ import annotations
import hashlib
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_KEYS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid","_hsenc","_hsmi"}

def normalize_url(url: str) -> str:
    """
    1) 스킴/호스트 lower
    2) 쿼리에서 추적 파라미터 제거 + key 정렬
    3) fragment(#...) 제거
    """
    p = urlparse(url)
    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower()
    # 쿼리 정리
    qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in TRACKING_KEYS]
    qs.sort(key=lambda kv: kv[0])
    query = urlencode(qs, doseq=True)
    # fragment 제거
    new = urlunparse((scheme, netloc, p.path or "", p.params or "", query, ""))  # no fragment
    return new

def make_url_key(url: str) -> str:
    """
    정규화된 URL의 SHA1(짧고 충돌위험 낮음) → 40자 hex
    """
    nurl = normalize_url(url)
    return hashlib.sha1(nurl.encode("utf-8")).hexdigest()

def normalize_text(s: str) -> str:
    """
    공백/개행/연속 스페이스 축약 → 해시 안정화용
    """
    s = s or ""
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sha256_hex(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

def body_checksum(body: str, title: str = "") -> str:
    """
    제목+본문을 합쳐 체크섬(변경 감지용)
    """
    norm = normalize_text(title) + "\n" + normalize_text(body)
    return sha256_hex(norm)
