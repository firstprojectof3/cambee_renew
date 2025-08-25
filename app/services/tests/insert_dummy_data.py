
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import User, Notice
from datetime import datetime

db: Session = SessionLocal()

db.query(Notice).delete()   # 공지 먼저 지우고
db.query(User).delete()     # 유저 지우고
db.commit()

# 테스트 유저
test_users = [
    User(
        user_id="2101001",
        name="이학사",
        student_number=2101001,  
        gender="F",
        grade=4,
        school="이화여자대학교",
        income_level=5,
        major="컴퓨터공학전공"
    ),
    User(
        user_id="2202002",
        name="박장학",
        student_number=2202002, 
        gender="F",
        grade=2,
        school="이화여자대학교",
        income_level=2,
        major="사학과"
    ),
    User(
        user_id="2303003",
        name="최식단",
        student_number=2303003,  
        gender="F",
        grade=1,
        school="이화여자대학교",
        income_level=6,
        major="경영학과"
    )
]




#사용자 조회 함수
def get_user_by_id(user_id: str) :
    return test_users.get(user_id)


# 삽입 실행
db.add_all(test_users)
db.add_all(test_notices)
db.commit()
print("테스트용 데이터 삽입 완료") 
db.close()
