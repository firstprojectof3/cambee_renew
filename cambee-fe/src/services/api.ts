// src/lib/api.ts
const BASE = "http://10.240.94.33:8000";

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