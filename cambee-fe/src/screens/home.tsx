// src/screens/home.tsx
import { View, Text, StyleSheet, Pressable, FlatList } from "react-native";
import ProfileCard from "../components/ProfileCard";
import AnswerCard from "../components/AnswerCard"; // 이미 만들었으면 재사용
const C={50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"};

const demoNotices=[ // 프리뷰용
  { title:"자료구조 보강 공지", link:"https://ex/1", summary:"금 15:00 온라인", content:"LMS 참고" },
  { title:"성적우수 장학 안내", link:"https://ex/2", summary:"신청 D-7", content:"평점 3.8+ 필요" },
];

export default function HomeScreen({ navigation }: any){
  return (
    <View style={st.container}>
      {/* 헤더 */}
      <View style={st.header}>
        <Text style={st.brand}>Cambee</Text>
        <Pressable onPress={()=>navigation.navigate("Chat")} style={st.askBtn}><Text style={st.askTxt}>챗으로 질문하기</Text></Pressable>
      </View>

      {/* 프로필 카드 */}
      <ProfileCard name="홍길동" school="OO대학교" dept="컴퓨터공학과" grade={3} sid="2020123456"/>

      {/* 섹션 타이틀 */}
      <Text style={st.secTitle}>공지 프리뷰</Text>

      {/* 공지 카드 리스트 (2개 프리뷰) */}
      <FlatList
        data={demoNotices}
        keyExtractor={(it)=>it.title}
        renderItem={({item})=><View style={{marginBottom:12}}><AnswerCard a={item as any}/></View>}
        scrollEnabled={false}
      />

      {/* 퀵액션 2개 */}
      <View style={st.actions}>
        <Pressable style={st.cardBtn} onPress={()=>navigation.navigate("Chat")}><Text style={st.cardBtnTxt}>공지 모아보기</Text></Pressable>
        <Pressable style={st.cardBtn} onPress={()=>navigation.navigate("Chat")}><Text style={st.cardBtnTxt}>시간표 가져오기</Text></Pressable>
      </View>
    </View>
  );
}

const st=StyleSheet.create({
  container:{ flex:1, backgroundColor:C[50], padding:16, gap:14 },
  header:{ flexDirection:"row", justifyContent:"space-between", alignItems:"center", marginTop: 10},
  brand:{ fontSize:22, fontWeight:"700", letterSpacing: 1.6, color:C[950] },
  askBtn:{ paddingVertical:8, paddingHorizontal:12, borderWidth:1, borderColor:C[600], borderRadius:12, backgroundColor:C[400] },
  askTxt:{ fontWeight:"900", color:C.white },

  secTitle:{ marginTop:6, marginBottom:4, fontSize:16, fontWeight:"900", color:C[700] },

  actions:{ flexDirection:"row", gap:12 },
  cardBtn:{ flex:1, padding:14, borderRadius:16, borderWidth:1, borderColor:C[800], backgroundColor:C.white, alignItems:"center" },
  cardBtnTxt:{ fontWeight:"900", color:C[950] },
});
