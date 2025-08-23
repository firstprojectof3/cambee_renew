# app/core/config.py
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List

# ──────────────────────────────────────────────────────────────
# .env 로드
# 프로젝트 루트 기준 .env 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"[WARN] .env 파일을 {ENV_PATH} 위치에서 찾지 못했습니다.")

# ──────────────────────────────────────────────────────────────
# 필수/공통 환경변수
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# 시스템 프롬프트
SYSTEM_PROMPT: Optional[str] = None
if os.getenv("SYSTEM_PROMPT"):
    SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
elif os.getenv("SYSTEM_PROMPT_FILE"):
    sp_file = BASE_DIR / os.getenv("SYSTEM_PROMPT_FILE")
    try:
        SYSTEM_PROMPT = sp_file.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"[WARN] SYSTEM_PROMPT_FILE 읽기 실패: {e}")

# ──────────────────────────────────────────────────────────────
# 크롤러/스케줄러 설정
def _parse_int(env_key: str, default: int) -> int:
    val = os.getenv(env_key, "").strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        print(f"[WARN] {env_key} 값이 정수가 아님: '{val}', 기본값 {default} 사용")
        return default

def _parse_list(env_key: str, default: List[str]) -> List[str]:
    raw = os.getenv(env_key, "")
    if not raw.strip():
        return default
    items = [s.strip() for s in raw.split(",")]
    return [s for s in items if s]

# 기본값: 이화여대 공지 메인
CRAWL_SEEDS: List[str] = _parse_list(
    "CRAWL_SEEDS",
    ["https://www.ewha.ac.kr/ewha/news/notice.do"]
)

# 분 단위 주기(기본 60분)
CRAWL_INTERVAL_MIN: int = _parse_int("CRAWL_INTERVAL_MIN", 60)

# 타임존(기본 Asia/Seoul)
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Seoul").strip() or "Asia/Seoul"

# ──────────────────────────────────────────────────────────────
# 확인 로그(민감정보는 노출하지 않음)
print("🔧 [CONFIG] DATABASE_URL =", "SET" if DATABASE_URL else "NOT SET")
print("🔧 [CONFIG] OPENAI_API_KEY =", "SET" if OPENAI_API_KEY else "NOT SET")
print("🔧 [CONFIG] SYSTEM_PROMPT =", "LOADED" if SYSTEM_PROMPT else "EMPTY")
print("🔧 [CONFIG] CRAWL_SEEDS =", CRAWL_SEEDS)
print("🔧 [CONFIG] CRAWL_INTERVAL_MIN =", CRAWL_INTERVAL_MIN)
print("🔧 [CONFIG] TIMEZONE =", TIMEZONE)
