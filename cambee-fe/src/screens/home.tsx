// src/screens/home.tsx
import React, { useEffect, useState } from "react";
import {
  View, Text, StyleSheet, Pressable, FlatList, SafeAreaView, Image, Alert, ScrollView
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import ProfileCard from "../components/ProfileCard";
import AnswerCard from "../components/AnswerCard";
import { loadUser, saveUser, clearUser } from "../state/auth";
import { fetchUser } from "../services/api";
import { StatusBar } from "expo-status-bar"; // ✅ 추가


const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};

const demoNotices = [
  { title:"자료구조 보강 공지", link:"https://ex/1", summary:"금 15:00 온라인", content:"LMS 참고" },
  { title:"성적우수 장학 안내", link:"https://ex/2", summary:"신청 D-7", content:"평점 3.8+ 필요" },
];

export default function HomeScreen({ navigation }: any) {
  const [user, setUser] = useState<any|null>(null);
  const [ready, setReady] = useState(false);

  useEffect(()=>{(async()=>{
  const sess = await loadUser();
  if(!sess) return navigation.replace("Auth");
  const fresh = await fetchUser(sess.user_id);
  setUser(fresh);
  await saveUser({ ...sess, ...fresh }); // 로컬도 최신화(선택)
  setReady(true);
})().catch(()=>navigation.replace("Auth"));},[]);

  if(!ready) return null;

  return (
    <SafeAreaView style={st.screen}>
      <StatusBar style="dark" backgroundColor={C[400]} />
      {/* Header */}
      <View style={st.headerWrap}>
        <View style={st.header}>
          <View style={st.hLeft}>
            <Image source={require("../../assets/app_logo.png")} style={st.logo} resizeMode="contain" />
            <Text style={st.brand}>CAMBEE</Text>
          </View>
          <View style={st.hRight}>
            <Pressable onPress={()=>{/* 알림 */}} style={st.iconBtn} hitSlop={8}>
              <Ionicons name="notifications-outline" size={22} color={C[950]} />
            </Pressable>
            <Pressable
              onPress={async ()=>{
                const ok = await new Promise<boolean>(res=>{
                  Alert.alert("로그아웃","정말 로그아웃할까요?",[
                    {  text:"취소", style:"cancel", onPress:()=>res(false) },
                    { text:"로그아웃", style:"destructive", onPress:()=>res(true) }
                  ]);
                });
                if(!ok) return;
                await clearUser();
                navigation.replace("Auth");
              }}
              style={st.iconBtn} hitSlop={8}>
              <Ionicons name="log-out-outline" size={22} color={C[950]} />
            </Pressable>
          </View>
        </View>
      </View>
        
      {/* Main (content width 제한) */}
      <ScrollView
        style={{flex:1}}
        contentContainerStyle={{ paddingHorizontal:16, paddingTop:14, paddingBottom:110, maxWidth:MAX_W, alignSelf:"center", width:"100%"}}
        showsVerticalScrollIndicator={false}
      >
        <ProfileCard user={user} onEdit={()=>navigation.navigate("ProfileEdit")} />
        <Text style={st.secTitle}>공지 프리뷰</Text>
          {demoNotices.map(it=>(
            <View key={it.link} style={{marginBottom:12}}>
              <AnswerCard a={it as any}/>
            </View>
          ))}
        </ScrollView>

      {/* Footer (gradient bar + 3 buttons) */}
      <LinearGradient
        colors={[C[200], C[300]]}
        start={{x:0.5, y:0}} end={{x:0.5, y:1}}
        style={st.footer}
      >
        <View style={st.footerInner}>
          <Pressable onPress={()=>{/* TODO: 캘린더 화면 */}} style={st.navBtn} hitSlop={10}>
            <Ionicons name="calendar-outline" size={22} color={C[950]} />
            <Text style={st.navTxt}>캘린더</Text>
          </Pressable>

          <Pressable onPress={()=>{/* 중앙 홈(유지) */}} style={st.navBtn} hitSlop={10}>
            <Ionicons name="home-outline" size={22} color={C[950]} />
            <Text style={st.navTxt}>홈</Text>
          </Pressable>

          <Pressable onPress={()=>navigation.navigate("Chat")} style={st.navBtn} hitSlop={10}>
            <Ionicons name="chatbubble-ellipses-outline" size={22} color={C[950]} />
            <Text style={st.navTxt}>챗</Text>
          </Pressable>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

const MAX_W = 720; // 메인 콘텐츠 최대 너비

const st = StyleSheet.create({
  screen:{ flex:1, backgroundColor:C[50] },

  // Header
  headerWrap:{ backgroundColor:C[400], borderBottomWidth:1, borderColor:C[600] },
  header:{
    flexDirection:"row", alignItems:"center", justifyContent:"space-between",
    paddingHorizontal:16, paddingVertical:10
  },
  hLeft:{ flexDirection:"row", alignItems:"center", gap:8 },
  logo:{ width:30, height:30 },
  brand:{ fontSize:20, fontWeight:"600", color:C[950], letterSpacing:1.2 },
  hRight:{ flexDirection:"row", alignItems:"center" },
  iconBtn:{ padding:8, marginLeft:4, borderRadius:10 },

  // Main content width 제한
  contentWrap:{
    flex:1, paddingHorizontal:16, paddingTop:14, paddingBottom:90,
    width:"100%", maxWidth:MAX_W, alignSelf:"center"
  },
  secTitle:{ marginLeft:5, marginTop:18, marginBottom:6, fontSize:16, fontWeight:"900", color:C[700] },

  // Footer
  footer:{
    position:"absolute", left:0, right:0, bottom:0,
    paddingTop:8, paddingBottom:16, borderTopWidth:1, borderColor:C[600]
  },
  footerInner:{
    flexDirection:"row", justifyContent:"space-around", alignItems:"center",
    paddingHorizontal:16, paddingTop:10
  },
  navBtn:{ alignItems:"center", gap:4 },
  navTxt:{ fontSize:12, fontWeight:"700", color:C[950] },
});
