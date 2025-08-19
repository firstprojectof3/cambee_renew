
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

test_notices = [
    # 학사 test
    Notice(
        category="학사",
        title="2025-2학기 학부 폐강 교과목 안내",
        content="2025-2학기 수강신청이 종료됨에 따라 폐강 처리된 교과목을 안내드립니다.",
        url="https://www.ewha.ac.kr/ewha/news/notice.do?mode=view&articleNo=356831&article.offset=0&articleLimit=10&srCategoryId1=25&no=21",
        date=datetime(2025, 8, 13),
        target_grade=None,
        target_major=None,
        target_student_number=None
    ),
    
    # 학사 test2
    Notice(
        category="학사",
        title="컴퓨터공학 전공인턴십 수강절차 안내",
        content="컴퓨터공학 인턴십 및 sw 산학실무 설계 교과목 수강 절차를 안내드립니다.",
        url="https://cse.ewha.ac.kr/cse/student/notice.do?mode=view&articleNo=638645&article.offset=10&articleLimit=10",
        date=datetime(2022, 2, 14),
        target_grade=None,
        target_major="컴퓨터공학전공",
        target_student_number=None
    ),
    


    # 장학 test
    Notice(
        category="장학",
        title="2025학년도 2학기 한국장학재단 국가장학금 2차 신청 안내",
        content="신입생 및 재학생을 위한 국가장학금 2차 신청 안내입니다.",
        url="https://www.ewha.ac.kr/ewha/news/notice.do?mode=view&articleNo=356694&article.offset=0&articleLimit=10&srCategoryId1=26&no=17",
        date=datetime(2025, 8, 7),
        target_grade=None,
        target_major=None,
        target_student_number=None
    ),

    # 식단 test
    Notice(
        category="식단",
        title="2025년 8월 2주차 진선미관 식단표",
        content="모든 학교 구성원을 위한 식단표 안내입니다.",
        url="https://www.ewha.ac.kr/ewha/life/restaurant.do?mode=view&articleNo=903&article.offset=0&articleLimit=10",
        date=datetime(2025, 8, 4),
        target_grade=None,             
        target_major=None,         
        target_student_number=None
        
        
              
    )
]




# 삽입 실행
db.add_all(test_users)
db.add_all(test_notices)
db.commit()
print("테스트용 데이터 삽입 완료") 
db.close()
