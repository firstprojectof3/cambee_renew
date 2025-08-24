// src/screens/setup.tsx
import React, { useState } from "react";
import { View, Text, Pressable, StyleSheet, Alert, Platform } from "react-native";
/// import DateTimePicker, { DateTimePickerEvent } from "@react-native-community/datetimepicker"; // expo install @react-native-community/datetimepicker
import { Ionicons } from "@expo/vector-icons";
import { savePrefs } from "../services/api";

const C={50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"};

const TAGS = ["학사","장학","식단","생활","편의시설"];

export default function SetupScreen({ route, navigation }: any){
  const { user_id } = route.params;
  const [selected, setSelected] = useState<string[]>([]);
  const [time, setTime] = useState(new Date()); // 기본 현재시간
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleTag = (t:string)=>{
    setSelected(prev => prev.includes(t) ? prev.filter(x=>x!==t) : [...prev, t]);
  };

  const onSave = async ()=>{
    if(!selected.length) return Alert.alert("알림","선호 주제를 하나 이상 선택해 주세요.");
    try{
      setLoading(true);
      const hh = time.getHours().toString().padStart(2,"0");
      const mm = time.getMinutes().toString().padStart(2,"0");
      await savePrefs({ 
        user_id, 
        preferred_topics: selected, 
        notification_time:`${hh}:${mm}`, 
        language:"ko" 
        });
      navigation.replace("Home");
    }catch(e:any){
      Alert.alert("오류", e?.message ?? "설정 저장 실패");
    }finally{ setLoading(false); }
  };

  return (
    <View style={st.wrap}>
      <Text style={st.h1}>초기 설정</Text>
      <Text style={st.sub}>선호 주제와 알림 시간을 선택하세요.</Text>

      <Text style={st.label}>선호 주제</Text>
      <View style={st.tagWrap}>
        {TAGS.map(t=>(
          <Pressable key={t} onPress={()=>toggleTag(t)} style={[st.tag, selected.includes(t) && st.tagSel]}>
            <Text style={[st.tagT, selected.includes(t)&&st.tagTSel]}>{t}</Text>
          </Pressable>
        ))}
      </View>

      <Text style={st.label}>알림 시간</Text>
<Pressable style={st.timeBtn} onPress={()=>setShow(true)}>
  <Ionicons name="time-outline" size={20} />
  <Text style={st.timeT}>
    {time.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"})}
  </Text>
</Pressable>
<Text style={st.sub}>매일 해당 시간에 알림을 받아요.</Text>

      <Pressable style={[st.btn, loading && {opacity:0.6}]} disabled={loading} onPress={onSave}>
        <Text style={st.btnT}>{loading ? "저장 중..." : "완료"}</Text>
      </Pressable>
    </View>
  );
}

const st=StyleSheet.create({
  wrap:{flex:1,backgroundColor:C[50],padding:16,gap:12,justifyContent:"center"},
  h1:{fontSize:22,fontWeight:"800",color:C[900]},
  sub:{color:C[700],marginBottom:10},
  label:{marginTop:8,fontWeight:"700",color:C[800]},
  tagWrap:{flexDirection:"row",flexWrap:"wrap",gap:8,marginTop:4},
  tag:{paddingVertical:8,paddingHorizontal:14,borderRadius:16,borderWidth:1,borderColor:C[800],backgroundColor:C.white},
  tagSel:{backgroundColor:C[500],borderColor:C[900]},
  tagT:{color:C[950],fontWeight:"600"},
  tagTSel:{color:C.white},
  timeBtn:{padding:12,borderRadius:12,borderWidth:1,borderColor:C[800],backgroundColor:C.white,alignItems:"center",marginTop:4},
  timeT:{fontSize:16,fontWeight:"700",color:C[900]},
  btn:{backgroundColor:C[600],padding:14,borderRadius:12,alignItems:"center",borderWidth:1.5,borderColor:C[800],marginTop:16},
  btnT:{fontWeight:"900",color:C.white},
});
