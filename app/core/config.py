import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

# 프로젝트 루트 기준 .env 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# .env 로드
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"[WARN] .env 파일을 {ENV_PATH} 위치에서 찾지 못했습니다.")

# 필수 환경변수
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# 시스템 프롬프트 처리
SYSTEM_PROMPT: Optional[str] = None

if os.getenv("SYSTEM_PROMPT"):
    SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
elif os.getenv("SYSTEM_PROMPT_FILE"):
    sp_file = BASE_DIR / os.getenv("SYSTEM_PROMPT_FILE")
    try:
        SYSTEM_PROMPT = sp_file.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"[WARN] SYSTEM_PROMPT_FILE 읽기 실패: {e}")

# 확인 로그
print("🔧 [CONFIG] DATABASE_URL =", "SET" if DATABASE_URL else "NOT SET")
print("🔧 [CONFIG] OPENAI_API_KEY =", "SET" if OPENAI_API_KEY else "NOT SET")
print("🔧 [CONFIG] SYSTEM_PROMPT =", "LOADED" if SYSTEM_PROMPT else "EMPTY")
