// src/screens/chat.tsx
import React, { useRef, useState, useEffect } from "react";
import {
  View, Text, TextInput, Pressable, FlatList, StyleSheet,
  KeyboardAvoidingView, Platform, Image, SafeAreaView
} from "react-native";
import MessageBubble from "../components/MessageBubble";

const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};
const BORDER = "#D0D0D0"; // 창 톤과 비슷한 살짝 어두운 회색

type Msg = { id:string; type:"user"|"bot"; text:string };

export default function ChatScreen({ navigation }: any){
  const [messages, setMessages] = useState<Msg[]>([
    { id:"welcome", type:"bot", text:"안녕하세요! 궁금한 걸 물어보세요 🐝" }
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<FlatList<Msg>>(null);
  const HEADER_H = 56;

  const send = () => {
    const t = input.trim();
    if (!t) return;
    const mine: Msg = { id: Date.now().toString(), type:"user", text: t };
    setMessages((m)=>[...m, mine]);
    setInput("");
    setTimeout(()=>{
      setMessages((m)=>[...m, { id: (Date.now()+1).toString(), type:"bot", text:"테스트 답변이에요 ✨" }]);
    }, 500);
  };

  useEffect(()=>{ listRef.current?.scrollToEnd({ animated:true }); }, [messages]);

  return (
    <SafeAreaView style={{flex:1, backgroundColor:"#FFF"}}>
    <KeyboardAvoidingView style={{ flex:1, backgroundColor:C.white }} behavior={Platform.OS==="ios"?"padding":undefined} keyboardVerticalOffset={0}>
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
       renderItem={({ item }) => (
  item.type==="user"
    ? <MessageBubble role="user">{item.text}</MessageBubble>
    : <MessageBubble role="assistant">{item.text}</MessageBubble>
)}
      />

      {/* 인풋 바(한 줄 배치) */}
      <View style={styles.inputRow}>
        <View style={styles.inputWrap}>
          <TextInput
            value={input}
            onChangeText={setInput}
            placeholder="메시지를 입력해 주세요…"
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

  bubble:{
    maxWidth:"78%", borderRadius:18, paddingVertical:10, paddingHorizontal:12, marginVertical:5,
    borderWidth:2, borderColor:C[950]
  },
  userBubble:{ alignSelf:"flex-end", backgroundColor:C[500] },
  botBubble:{ alignSelf:"flex-start", backgroundColor:C[100] },
  userText:{ color:C.white, fontSize:16, fontWeight:"700" },
  botText:{ color:C[950], fontSize:16, fontWeight:"600" },

  // === 인풋/전송: 같은 라인, 여유 간격, 얇은 보더 ===
  inputRow:{
    flexDirection:"row", alignItems:"center", justifyContent:"center",
    gap:10, padding:10, backgroundColor:C.white
  },
  inputWrap:{
    flex:1, marginLeft:12, marginRight:0,
    minHeight:48, maxHeight:120,
    backgroundColor:C.white,
    borderRadius:18,
    borderWidth:1, borderColor:BORDER, // ✅ 1px, 연회색
    paddingHorizontal:12, paddingVertical:8,
    shadowColor:"#000", shadowOpacity:0.06, shadowRadius:6, shadowOffset:{ width:0, height:3 },
    elevation:1,
    justifyContent:"center"
  },
  input:{ fontSize:16, padding:0, marginLeft:9},

  sendBtn:{
    marginRight:12,
    height:48, minWidth:72,
    paddingHorizontal:16,
    borderRadius:24,
    backgroundColor:C[600],
    alignItems:"center", justifyContent:"center",
    borderWidth:1, borderColor:C[700], // ✅ 1px, 연회색
  },

});


