// src/screens/register2.tsx
import React, { useState } from "react";
import {
  View, Text, TextInput, Pressable, StyleSheet, Alert,
  KeyboardAvoidingView, Platform, ScrollView
} from "react-native";
import { updateUser } from "../services/api";

const C={50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"};

const clamp=(n:number,min:number,max:number)=>Math.min(Math.max(n,min),max);
const isInt=(s:string)=>/^\d+$/.test(s||"");

export default function Register2Screen({ route, navigation }: any){
  const { user_id } = route.params;

  const [name, setName] = useState("");
  const [student_number, setSid] = useState("");
  const [gender, setGender] = useState<"M"|"F"|"X"|"">("");
  const [grade, setGrade] = useState("");
  const [school, setSchool] = useState("");
  const [income_level, setIncome] = useState("");
  const [major, setMajor] = useState("");
  const [loading,setLoading] = useState(false);

  const validate=()=>{
    if(!name||!student_number||!gender||!grade||!school||!income_level||!major){
      Alert.alert("알림","모든 항목을 입력해 주세요."); return false;
    }
    if(!isInt(student_number)) { Alert.alert("알림","학번은 숫자만 입력해 주세요."); return false; }
    if(!isInt(grade) || clamp(+grade,1,6)!==+grade){ Alert.alert("알림","학년은 1~4 사이 숫자입니다."); return false; }
    if(!isInt(income_level) || clamp(+income_level,1,10)!==+income_level){ Alert.alert("알림","소득분위는 1~10 사이 숫자입니다."); return false; }
    return true;
  };

  const onNext = async ()=>{
    if(!validate()) return;
    try{
      setLoading(true);
      await updateUser(user_id, {
        name,
        student_number: parseInt(student_number,10),
        gender,                              // "M" | "F" | "X"
        grade: parseInt(grade,10),           // 1~6
        school,
        income_level: parseInt(income_level,10), // 1~10
        major,
      });
      navigation.replace("Setup", { user_id });
    }catch(e:any){
      Alert.alert("오류", e?.message ?? "업데이트 실패");
    }finally{ setLoading(false); }
  };

  const GOpt=({v,label}:{v:"M"|"F"|"X";label:string})=>(
    <Pressable onPress={()=>setGender(v)} style={[st.gOpt, gender===v && st.gOptSel]}>
      <Text style={[st.gOptT, gender===v && st.gOptTSel]}>{label}</Text>
    </Pressable>
  );

  return (
    <KeyboardAvoidingView behavior={Platform.select({ios:"padding"})} style={{flex:1}}>
      <ScrollView contentContainerStyle={st.wrap} keyboardShouldPersistTaps="handled">
        <Text style={st.h1}>프로필을 생성합니다.</Text> 
        <Text style={st.h1}>개인정보를 입력해주세요.</Text>

        <TextInput style={st.inp} placeholder="이름" value={name} onChangeText={setName}/>
        <TextInput style={st.inp} placeholder="학교" value={school} onChangeText={setSchool}/>
        <TextInput style={st.inp} placeholder="전공" value={major} onChangeText={setMajor}/>

        <TextInput style={st.inp} placeholder="학번(숫자)" keyboardType="number-pad"
          value={student_number} onChangeText={setSid}/>

        <TextInput style={st.inp} placeholder="학년(1~4)"  keyboardType="number-pad"
          value={grade} onChangeText={setGrade}/>

        <TextInput style={st.inp} placeholder="소득분위(1~10)" keyboardType="number-pad"
          value={income_level} onChangeText={setIncome}/>

        <Text style={st.label}>성별</Text>
        <View style={st.gRow}>
          <GOpt v="M" label="M" />
          <GOpt v="F" label="F" />
          <GOpt v="X" label="기타" />
        </View>

        <Pressable style={[st.btn, loading && {opacity:0.6}]} disabled={loading} onPress={onNext}>
          <Text style={st.btnT}>{loading ? "저장 중..." : "다음"}</Text>
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const st=StyleSheet.create({
  wrap:{flexGrow:1, padding:16, gap:12, backgroundColor:C[50], justifyContent:"center"},
  h1:{fontSize:22, fontWeight:"800", color:C[900], marginBottom:6},
  inp:{borderWidth:1, borderColor:"#ddd", borderRadius:14, padding:12, backgroundColor:C.white},
  label:{marginTop:4, fontWeight:"700", color:C[800]},
  gRow:{flexDirection:"row", gap:8},
  gOpt:{flex:1, paddingVertical:12, borderRadius:12, borderWidth:1, borderColor:C[800], backgroundColor:C.white, alignItems:"center"},
  gOptSel:{backgroundColor:C[500], borderColor:C[900]},
  gOptT:{fontWeight:"700", color:C[950]},
  gOptTSel:{color:C.white},
  btn:{backgroundColor:C[600], padding:14, borderRadius:12, alignItems:"center", borderWidth:1.5, borderColor:C[800], marginTop:4},
  btnT:{fontWeight:"900", color:C.white},
});
