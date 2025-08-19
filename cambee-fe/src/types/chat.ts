// src/types/chat.ts
export type Role = "user" | "assistant";
export type Answer = { title:string; link:string; summary:string; content:string };
export type Message =
  | { id:string; role:"user"; text:string }
  | { id:string; role:"assistant"; text?:string; answer?:Answer };
