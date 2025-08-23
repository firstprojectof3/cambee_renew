# app/crawler/sites/ewha_notice.py
from __future__ import annotations
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from dateutil import parser as dateparser
from typing import List, Dict, Optional

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CambeeCrawler/0.1; +https://example.invalid)"
}

# --- 유틸 ---

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _to_abs(base: str, href: str) -> str:
    try:
        return urljoin(base, href)
    except Exception:
        return href

def _parse_date(txt: str) -> Optional[datetime]:
    """
    날짜 텍스트를 date/datetime으로 파싱.
    기대 포맷 예: 2025-08-12, 2025.08.12, 2025/08/12, '2025-08-12 14:30' 등
    """
    txt = _clean(txt)
    # 흔한 구분자 치환
    txt = txt.replace("년", "-").replace("월", "-").replace("일", "").replace(".", "-").replace("/", "-")
    try:
        dt = dateparser.parse(txt, yearfirst=True, dayfirst=False, fuzzy=True)
        return dt
    except Exception:
        return None

# --- 메인: 공지 리스트 파서 ---

def fetch_notice_list(list_url: str, page: Optional[int] = None) -> List[Dict]:
    """
    이화여대 공지 목록 페이지에서
    [{title, link, posted_at(YYYY-MM-DD), category}] 추출.

    - page 인자를 사용하는 사이트면 쿼리스트링으로 추가 시도.
    - 테이블형/리스트형 모두 대응하는 범용 로직.
    """
    url = list_url
    # 페이지 파라미터가 필요한 경우(있다면) 붙이기: page, pageNo, curPage 등 흔한 키 시도
    if page is not None:
        if "?" in url:
            url += f"&page={page}"
        else:
            url += f"?page={page}"

    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
    resp.raise_for_status()

    # 인코딩 보정
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, "lxml")

    items = []

    # 1) 테이블 형태: <table> ... <tbody><tr>...</tr>
    table = soup.find("table")
    if table:
        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            # 제목/링크
            a = tr.find("a", href=True)
            if not a:
                continue
            title = _clean(a.get_text(" ", strip=True))
            link = _to_abs(url, a["href"])

            # 카테고리/날짜 컬럼 추정
            tds = tr.find_all("td")
            posted_at = None
            category = ""

            # 날짜 후보: td 텍스트 중 '2025', '2024' 등 연도 포함 & 숫자/구분자 비율 높은 것
            for td in reversed(tds):
                txt = _clean(td.get_text(" ", strip=True))
                if re.search(r"\b20\d{2}\b", txt):
                    d = _parse_date(txt)
                    if d:
                        posted_at = d.date().isoformat()
                        break

            # 카테고리 후보: '공지', '학사', '장학' 같은 짧은 텍스트 컬럼
            for td in tds:
                txt = _clean(td.get_text(" ", strip=True))
                if 1 <= len(txt) <= 6 and not re.search(r"\d{4}", txt):
                    # 제목과 너무 비슷하면 스킵
                    if txt and txt not in title and not posted_at:
                        category = txt
                        break

            items.append({
                "title": title,
                "link": link,
                "posted_at": posted_at,   # YYYY-MM-DD or None
                "category": category or None
            })

    # 2) 리스트(ul/li) 형태: <ul class="..."><li> ... <a>제목</a> ... <span class="date">...</span>
    if not items:
        uls = soup.find_all("ul")
        for ul in uls:
            for li in ul.find_all("li", recursive=False) or []:
                a = li.find("a", href=True)
                if not a:
                    continue
                title = _clean(a.get_text(" ", strip=True))
                link = _to_abs(url, a["href"])

                # 날짜/카테고리 추정
                posted_at = None
                category = None

                # 클래스 네이밍 힌트 기반
                date_node = li.find(class_=re.compile(r"(date|time)", re.I))
                if date_node:
                    d = _parse_date(date_node.get_text(" ", strip=True))
                    if d:
                        posted_at = d.date().isoformat()

                cat_node = li.find(class_=re.compile(r"(cat|category|label|tag)", re.I))
                if cat_node:
                    category = _clean(cat_node.get_text(" ", strip=True)) or None

                # 없으면 텍스트 덩어리에서 날짜 스캔
                if not posted_at:
                    blob = _clean(li.get_text(" ", strip=True))
                    m = re.search(r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2})", blob)
                    if m:
                        d = _parse_date(m.group(1))
                        if d:
                            posted_at = d.date().isoformat()

                items.append({
                    "title": title,
                    "link": link,
                    "posted_at": posted_at,
                    "category": category
                })

    # 중복/노이즈 정리: 제목/링크 없는 것 제거, 링크 기준으로 유일화
    dedup = {}
    for it in items:
        if not it.get("title") or not it.get("link"):
            continue
        key = it["link"]
        if key not in dedup:
            dedup[key] = it
    items = list(dedup.values())

    return items


# --- 상세 본문 추출 공통 유틸 ---

def _extract_main_block(soup: BeautifulSoup) -> str:
    # 1) 잡다한 태그 제거
    for t in soup(["script", "style", "noscript"]):
        t.decompose()

    # 2) 대표 블록 후보 우선순위: article > main > section > div
    candidates = []
    for name in ["article", "main", "section", "div"]:
        for tag in soup.find_all(name):
            txt = _clean(tag.get_text(" ", strip=True))
            candidates.append((len(txt), txt))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        body = candidates[0][1]
    else:
        body = _clean(soup.get_text(" ", strip=True))
    return body

def _collect_attachments(soup: BeautifulSoup, base_url: str):
    files = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = _clean(a.get_text(" ", strip=True)) or href.rsplit("/", 1)[-1]
        abs_url = _to_abs(base_url, href)
        # 첨부로 볼만한 패턴만 수집(확장자/다운로드 경로 힌트)
        if re.search(r"(\.(pdf|hwp|hwpx|docx?|pptx?|xlsx?)$)|download|attach|attachment", href, re.I):
            files.append({"name": name[:120], "href": abs_url})
    # 중복 제거
    dedup = {}
    for f in files:
        if f["href"] not in dedup:
            dedup[f["href"]] = f
    return list(dedup.values())

# --- 상세 페이지 파서 ---

def fetch_notice_detail(detail_url: str) -> Dict:
    """
    상세 페이지에서 {"title","body","attachments":[...],"posted_at":YYYY-MM-DD} 추출
    """
    resp = requests.get(detail_url, headers=DEFAULT_HEADERS, timeout=12)
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, "lxml")

    # 제목
    title = ""
    if soup.title:
        title = _clean(soup.title.get_text(" ", strip=True))
    h1 = soup.find(["h1","h2"])
    if h1:
        h1_txt = _clean(h1.get_text(" ", strip=True))
        # title이 너무 길거나 빈약하면 헤딩으로 교체
        if 5 <= len(h1_txt) <= 200:
            title = h1_txt or title

    # 날짜 (상세에 있으면 목록값 보완)
    posted_at = None
    date_node = soup.find(class_=re.compile(r"(date|time|posted|reg)", re.I)) or \
                soup.find(string=re.compile(r"20\d{2}[\./-]\d{1,2}[\./-]\d{1,2}"))
    if date_node:
        d = _parse_date(date_node.get_text(" ", strip=True) if hasattr(date_node, "get_text") else str(date_node))
        if d:
            posted_at = d.date().isoformat()

    # 본문
    body = _extract_main_block(soup)

    # 첨부
    attachments = _collect_attachments(soup, detail_url)

    return {
        "title": title,
        "body": body,
        "attachments": attachments,
        "posted_at": posted_at
    }
