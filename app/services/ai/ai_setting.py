from openai import OpenAI
from dotenv import load_dotenv
import os
# pip install --upgrade openai

load_dotenv()  # 환경 변수 로드

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(client, messages):
    return client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,  # 지시를 더 잘 따르게
        max_tokens=1000,  # 충분한 길이 확보
        # response_format="json"
    )
