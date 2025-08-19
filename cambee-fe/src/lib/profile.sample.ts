// src/lib/profile.sample.ts
import { ChatPayload } from "../types/chat";

export const PROFILE: Omit<ChatPayload, "message"> = {
  user_id: "2101001",
  major: "컴퓨터공학전공",
  grade: 4,
  school: "이화여자대학교",
  income_level: 5
} as const;

/*
// 다른 예시 유저들 (필요하면 이거ss 풀어서 사용)

export const PROFILE2: Omit<ChatPayload, "message"> = {
  user_id: "2303029",
  major: "사학과",
  grade: 2,
  school: "이화여자대학교",
  income_level: 2,
} as const;

export const PROFILE3: Omit<ChatPayload, "message"> = {
  user_id: "2501001",
  major: "경영학과", // 원래 usersdb 내용 이어붙여야 함
  grade: 1,
  school: "이화여자대학교",
  income_level: 6, // 아직 값 잘림 → 확인 필요
} as const;
*/