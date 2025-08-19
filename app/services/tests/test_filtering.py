from app.database import SessionLocal
from app.models.models import User, Notice
from app.crud import filter_notices_by_user_info

# 테스트 유저 리스트
test_users_ids = ["2101001", "2202002", "2303003"]

# DB 세션 시작
db = SessionLocal()
try:
    for user_id in test_users_ids:
        print("\n" + "-" * 70)
        print(f"👤 [유저 {user_id}]")

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            print("❌ 유저 없음")
            continue

        # 필요시 최근 200건만 테스트하려면 주석 해제
        # all_notices = db.query(Notice).order_by(Notice.created_at.desc()).limit(200).all()
        all_notices = db.query(Notice).all()

        filtered, dropped = filter_notices_by_user_info(
            user, all_notices, debug=True, return_both=True
        )
        print(f"✅ 통과 {len(filtered)}건 / 🚫 제외 {len(dropped)}건")

        if not filtered:
            print("📭 해당 유저에게 맞는 공지 없음")
        else:
            for notice in filtered:
                print(f"📌 {notice.title} | {notice.category} | {notice.url}")

        # =========================
        # 🔍 제외된 공지 원시 타겟 필드값 출력 (원인 파악용)
        # =========================
        for item in dropped:
            n = item["notice"]
            reasons = ", ".join(item["reasons"])
            print("-" * 70)
            print(f"🪵 제외 공지: {getattr(n, 'title', '(제목없음)')}")
            print(f"   사유: {reasons}")
            print(f"   target_major: {repr(getattr(n, 'target_major', None))}")
            print(f"   target_grade: {repr(getattr(n, 'target_grade', None))}")
            print(f"   target_student_number: {repr(getattr(n, 'target_student_number', None))}")
            print(f"   category: {repr(getattr(n, 'category', None))}")

finally:
    db.close()
