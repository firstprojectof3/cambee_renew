// src/services/api.ts
const BASE = "https://shiny-parakeet-7vwq5xq49995crj67-8000.app.github.dev/api";

export async function sendChat(p: any) {
  const url = `${BASE}/chat`;

  console.log("🚀 [sendChat] POST 요청");
  console.log("URL:", url);
  console.log("Payload:", p);

  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    });

    console.log("📡 Response status:", r.status);

    const raw = await r.text();  // 일단 raw로 받아서 확인
    console.log("📦 Raw response:", raw);

    if (!r.ok) throw new Error(`HTTP ${r.status}: ${raw}`);

    const data = JSON.parse(raw);
    console.log("✅ Parsed response:", data);

    return data;
  } catch (e) {
    console.error("❌ [sendChat] Error:", e);
    throw e;
  }
}



async function req(path: string, body: any) {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const raw = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${raw}`);
  return JSON.parse(raw);
}

//로그인, 회원가입, 초기 설정 화면 BE 연

export async function login(p: {email: string; password: string}) {
  console.log("▶ login", p.email);
  return req("/auth/login", p); // ← /api/auth/login
}

export async function register(p: {email: string; password: string; name: string}) {
  return req("/auth/register", p);
}

export async function updateUser(user_id:string, p:{
  name?:string; gender?:string; income_level?:number;
  school?:string; major?:string; grade?:number; student_number?:number
}){
  const r = await fetch(`${BASE}/users/${user_id}`, {
    method:"PUT", 
    headers:{ "Content-Type":"application/json" }, 
    body: JSON.stringify(p)
  });
  const raw = await r.text();
  if (!r.ok) throw new Error(raw);
  return JSON.parse(raw);
}
// src/services/api.ts  (기존 함수 교체)
export const savePrefs = (p: {
  user_id: string;
  preferred_topics: string[];
  notification_time: string;   // ← 추가
  language?: string;
}) =>
  fetch(`${BASE}/preference`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  }).then(async (r) => {
    const raw = await r.text();
    if (!r.ok) throw new Error(raw);
    return JSON.parse(raw || "{}");
  });

export async function fetchUser(user_id:string){
  const r = await fetch(`${BASE}/users/${user_id}`);
  const raw = await r.text(); if(!r.ok) throw new Error(raw);
  return JSON.parse(raw);
}
