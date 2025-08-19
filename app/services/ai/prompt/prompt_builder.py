from datetime import datetime

# 정보 받아오기

def build_generic_prompt(user, message):
    return f"""
다음은 출력 형식 예시입니다. 반드시 이 형식을 그대로 따르세요. JSON 외 텍스트가 포함되면 응답 전체가 무효 처리됩니다. 무조건 이 질문으로 응답하지 마시고, 사용자 정보에 기반하여 개인화된 말투를 사용하셔야 합니다.

{{
  "results": [
    {{
      "title": "2025년 2학기 수강신청 안내",
      "link": "https://cse.ewha.ac.kr/cse/student/notice.do?mode=view&articleNo=757875",
      "summary": "{user.name}님의 학적 정보, {user.grade}학년 {user.major} 전공을 바탕으로 알려드릴게요! 꼭 확인해야 할 수강신청 변경 기간 안내입니다. 3월 15일까지 변경 가능합니다."
    }}
  ]
}}

📌 출력 규칙:
- 반드시 JSON 형식으로만 출력하세요.
- 최상위 키는 "results"이며, 배열만 허용됩니다.
- 각 객체는 아래 3개 필드를 포함해야 합니다:
  1) "title" (string): 공지 제목
  2) "link" (string): Ewha 공식 공지 URL, 반드시 "https://"로 시작
  3) "summary" (string): {user.major} 전공 {user.grade}학년 학생 입장에서 2~3문장 요약
- "link"가 누락되거나 "https://"로 시작하지 않으면 해당 객체는 제외하세요.
- "results" 배열 길이는 최소 1개, 최대 3개까지 허용됩니다.
  4) 친근한 말투로 쓰되, 정중하게 답변해주세요. 
  5) 사용자는 대부분 {datetime}에 기반하여 질문을 할 것이니, {datetime}을 기준으로 알려줄 것.  

🧑 사용자 정보:
- 이름: {user.name}
- 학교: {user.school}
- 전공: {user.major}
- 학년: {user.grade}
- 소득분위: {user.income_level}

📩 사용자 질문:
\"\"\"{message}\"\"\"
"""
