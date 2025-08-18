// src/screens/chat.tsx
import React, { useRef, useState, useEffect } from "react";
import {
  View, Text, TextInput, Pressable, FlatList, StyleSheet,
  KeyboardAvoidingView, Platform, Image, SafeAreaView, Linking, ListRenderItem
} from "react-native";
import MessageBubble from "../components/MessageBubble";
import { OUTPUT_SAMPLE } from "../lib/output.sample";

const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};
const BORDER = "#D0D0D0";

type Msg = {
  id: string;
  type: "user" | "assistant";
  text?: string;          // 일반 텍스트 응답
  title?: string;         // 카드형 응답용
  summary?: string;
  link?: string;
};

export default function ChatScreen({ navigation }: any){
  const [messages, setMessages] = useState<Msg[]>([
    { id:"welcome",
      type:"assistant",
      text:"안녕하세요! 1~4번 중 하나를 입력해 보세요 🐝"
    }
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<FlatList<Msg>>(null);

  const send = () => {
    const t = input.trim();
    if (!t) return;

    // 1) 내 메시지
    const mine: Msg = { id: Date.now().toString(), type:"user", text: t };
    setMessages(m => [...m, mine]);
    setInput("");

    // 2) 간단 매핑: "1"~"4" → OUTPUT_SAMPLE 사용
    const data = OUTPUT_SAMPLE[t as keyof typeof OUTPUT_SAMPLE];
    if (data) {
      // 카드형(assistant) 응답: title/summary/link 채워서 렌더
      const bot: Msg = {
        id: (Date.now()+1).toString(),
        type: "assistant",
        title: data.title,
        summary: data.summary,
        link: data.link
      };
      setMessages(m => [...m, bot]);
    } else {
      // 일반 텍스트 응답
      const bot: Msg = {
        id: (Date.now()+1).toString(),
        type: "assistant",
        text: "해당 번호에 맞는 공지가 없어요 😅 (1~4를 입력해 보세요)"
      };
      setMessages(m => [...m, bot]);
    }
  };

  useEffect(() => {
    listRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const renderItem: ListRenderItem<Msg> = ({ item }) => {
    if (item.type === "user" && item.text) {
      return <MessageBubble role="user">{item.text}</MessageBubble>;
    }
    if (item.type === "assistant") {
      // 카드형 출력 (title/summary/link가 있을 때)
      if (item.title && item.summary && item.link) {
        return (
          <MessageBubble role="assistant">
            <>
              <Text style={{ fontWeight:"700", fontSize:17}}>
                📖{item.title}
              </Text>
              <View style={{ height:1, backgroundColor:"#d1c269ff", marginVertical:10, marginHorizontal: 3 }} />
              <Text style={{ marginBottom:6 }}>🏷️{item.summary}</Text>
              <Text
                style={{ color:"#8b400e94", textDecorationLine:"underline" }}
                onPress={() => Linking.openURL(item.link!)}
              >
                🔗자세한 내용은 이 링크를 참고해주세요
              </Text>
            </>
          </MessageBubble>
        );
      }
      // 일반 텍스트 출력
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
              placeholder="번호를 입력해 주세요 (1~4)"
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
