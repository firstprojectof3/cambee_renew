// src/screens/chat.tsx
import React, { useRef, useState, useEffect } from "react";
import {
  View, Text, TextInput, Pressable, FlatList, StyleSheet,
  KeyboardAvoidingView, Platform, Image, SafeAreaView, Linking, ListRenderItem
} from "react-native";
import MessageBubble from "../components/MessageBubble";
import { sendChat } from "../services/api";  // API 호출 함수
import { PROFILE } from "../lib/profile.sample";


const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};
const BORDER = "#D0D0D0";

type Answer = { title:string; summary:string; link:string };
type Msg = { id:string; type:"user"|"assistant"; text?:string; answer?:Answer };

function normalizeResult(results: any): {text?:string; answer?:Answer} {
  try {
    // 문자열인데 객체 형태면 파싱
    if (typeof results === "string" && results.trim().startsWith("{")) {
      results = JSON.parse(results);
    }
  } catch {}
  // 객체에 title/summary/link 있으면 카드
  if (results && typeof results === "object" && results.title && results.summary && results.link) {
    return { answer: { title: results.title, summary: results.summary, link: results.link } };
  }
  // 그 외는 텍스트
  return { text: typeof results === "string" ? results : JSON.stringify(results) };
}

export default function ChatScreen({ navigation }: any){
  const [messages, setMessages] = useState<Msg[]>([
    { id:"welcome",
      type:"assistant",
      text:"안녕하세요! 질문을 입력해 보세요 🐝"
    }
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<FlatList<Msg>>(null);

  const send = async () => {
  const t = input.trim(); if (!t) return;
  setMessages(m=>[...m, { id:Date.now()+"", type:"user", text:t }]);
  setInput("");

    // ✅ 프로필 + message 합쳐서 payload 만들기
  const payload = { ...PROFILE, message: t };
  console.log("payload -> ", payload);

  try {
    const res = await sendChat(payload);
    const norm = normalizeResult(res.results);
    setMessages((m)=>[
      ...m,
      norm.answer ? { id:Date.now()+"a", type:"assistant", ...norm.answer } : { id:Date.now()+"b", type:"assistant", text:norm.text }
    ]);
  } catch {
    setMessages(m=>[...m, { id:Date.now()+"e", type:"assistant", text:"서버 오류가 발생했어요 😢"}]);
  }
};


  useEffect(() => {
    listRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const renderItem: ListRenderItem<Msg> = ({ item }) => {
  if (item.type==="user" && item.text) return <MessageBubble role="user">{item.text}</MessageBubble>;
  if (item.type==="assistant") {
    if (item.answer) {
      return (
        <MessageBubble role="assistant">
          <>
            <Text style={{ fontWeight:"700", fontSize:17 }}>📖 {item.answer.title}</Text>
            <View style={{ height:1, backgroundColor:"#d1c269ff", marginVertical:10, marginHorizontal:6 }} />
            <Text style={{ marginBottom:6 }}>🏷️ {item.answer.summary}</Text>
            <Text
              style={{ color:"#545727ff", textDecorationLine:"underline" }}
              onPress={() => Linking.openURL(item.answer!.link)}
            >
              🔗 자세히 보기
            </Text>
          </>
        </MessageBubble>
      );
    }
    return <MessageBubble role="assistant">{item.text ?? ""}</MessageBubble>;
  }
  return null;
};

  return (
    <SafeAreaView style={{flex:1, backgroundColor:"#FFF"}}>
      <KeyboardAvoidingView
        style={{ flex:1, backgroundColor:C.white }}
        behavior={Platform.OS==="ios" ? "padding" : undefined}
        keyboardVerticalOffset={0}
      >
        {/* 헤더 */}
        <View style={styles.header}>
          <Pressable onPress={()=>navigation.goBack()} hitSlop={10} style={styles.hBtn}>
            <Text style={styles.hIcon}>←</Text>
          </Pressable>
          <Image source={require("../../assets/app_logo.png")} style={styles.hLogo} resizeMode="contain" />
          <Pressable onPress={()=>{}} hitSlop={10} style={styles.hBtn}>
            <Text style={styles.hIcon}>🗂️</Text>
          </Pressable>
        </View>

        {/* 리스트 */}
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(it)=>it.id}
          contentContainerStyle={{ paddingHorizontal:16, paddingTop:12, paddingBottom:8 }}
          renderItem={renderItem}
        />

        {/* 인풋 바 */}
        <View style={styles.inputRow}>
          <View style={styles.inputWrap}>
            <TextInput
              value={input}
              onChangeText={setInput}
              placeholder="질문을 입력해 주세요"
              placeholderTextColor={C[800]}
              style={styles.input}
              multiline
            />
          </View>
          <Pressable onPress={send} style={styles.sendBtn}>
            <Text style={{ color:C.white, fontWeight:"800" }}>전송</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  header:{
    height:56, flexDirection:"row", alignItems:"center", justifyContent:"space-between",
    paddingHorizontal:12, backgroundColor:C.white,
    borderBottomWidth:1, borderBottomColor:"#E5E5E5"
  },
  hBtn:{ width:40, alignItems:"center", justifyContent:"center" },
  hIcon:{ fontSize:24, color:C[950], fontWeight:"900" },
  hLogo:{ width:40, height:40 },

  inputRow:{
    flexDirection:"row", alignItems:"center", justifyContent:"center",
    gap:10, padding:10, backgroundColor:C.white, borderTopWidth:1, borderTopColor:"#E5E5E5"
  },
  inputWrap:{
    flex:1, marginLeft:12,
    minHeight:48, maxHeight:120,
    backgroundColor:C.white,
    borderRadius:18,
    borderWidth:1, borderColor:BORDER,
    paddingHorizontal:12, paddingVertical:8,
    shadowColor:"#000", shadowOpacity:0.06, shadowRadius:6, shadowOffset:{ width:0, height:3 },
    elevation:1,
    justifyContent:"center"
  },
  input:{ fontSize:16, padding:0, marginLeft:9 },
  sendBtn:{
    marginRight:12,
    height:48, minWidth:72, paddingHorizontal:16,
    borderRadius:24, backgroundColor:C[600],
    alignItems:"center", justifyContent:"center",
    borderWidth:1, borderColor:C[700],
  },
});
