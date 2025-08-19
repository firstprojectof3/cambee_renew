// src/lib/router.ts
import { Answer } from "../types/chat";

const DB: Record<string, Answer> = {
  장학금: { title:"성적우수 장학", link:"https://ex/2", summary:"신청 오픈 / D-7", content:"평점 3.8+, 15학점 이상." },
  보강: { title:"자료구조 보강", link:"https://ex/1", summary:"금 15:00 온라인", content:"ZOOM 링크는 LMS 참고." },
};

export function route(input: string): { text?: string; answer?: Answer } {
  for (const k of Object.keys(DB)) if (input.includes(k)) return { answer: DB[k] };
  return { text: "해당 키워드로 찾은 공지가 없어. 다른 표현으로 물어볼래?" };
}
