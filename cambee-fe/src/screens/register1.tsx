// src/screens/register1.tsx
import React, { useRef, useState } from "react";
import {
  View, Text, StyleSheet, TextInput, Pressable, Animated, Easing,
  KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator, Alert
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { register, login } from "../services/api";
import { saveUser } from "../state/auth";

const C = {50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"};
const emailOK = (s:string)=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);

export default function Register1Screen({ navigation }: any){
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [email,setEmail] = useState("");
  const [pw,setPw] = useState("");
  const [pw2,setPw2] = useState("");

  // focus anims
  const makeAV = () => useRef(new Animated.Value(0)).current;
  const f1=makeAV(), f2=makeAV(), f3=makeAV(), f4=makeAV();
  const animate = (v: Animated.Value, to: 0|1) =>
    Animated.timing(v,{ toValue:to, duration:160, easing:Easing.out(Easing.quad), useNativeDriver:false }).start();
  const b = (v: Animated.Value)=>v.interpolate({ inputRange:[0,1], outputRange:[C[200], C[500]] });
  const bg= (v: Animated.Value)=>v.interpolate({ inputRange:[0,1], outputRange:[C.white, C[50]] });

  const onSubmit = async () => {
    // ✅ 유효성(모두 Alert로 피드백)
    if(!name || !email || !pw || !pw2) return Alert.alert("알림","이름/이메일/비밀번호를 입력해 주세요.");
    if(!emailOK(email)) return Alert.alert("알림","올바른 이메일 형식이 아니에요.");
    if(pw.length < 8) return Alert.alert("알림","비밀번호는 8자 이상이어야 해요.");
    if(pw !== pw2) return Alert.alert("알림","비밀번호가 일치하지 않아요.");

    try{
      setLoading(true);
      await register({ email, password: pw, name });      // 1) 가입
      const res = await login({ email, password: pw });   // 2) 즉시 로그인
      await saveUser(res.user);                            // 3) 로컬 저장
      navigation.replace("Register2", { user_id: res.user.user_id }); // 4) 다음 단계
    }catch(e:any){
      Alert.alert("오류", e?.message ?? "회원가입/로그인에 실패했어요.");
    }finally{
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient colors={[C[50], C[100], C[50]]} locations={[0,0.6,1]} start={{x:0.5,y:0}} end={{x:0.5,y:1}} style={StyleSheet.absoluteFill} />
      <KeyboardAvoidingView behavior={Platform.select({ ios:"padding" })} style={{flex:1}}>
        <View style={styles.header}><Text style={styles.headerTitle}>회원가입</Text></View>

        <ScrollView contentContainerStyle={styles.scrollInner} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          <View style={styles.form}>
            <Animated.View style={[styles.field,{ borderColor:b(f1), backgroundColor:bg(f1)}]}>
              <TextInput
                placeholder="이름" placeholderTextColor={C[800]}
                value={name} onChangeText={setName}
                onFocus={()=>animate(f1,1)} onBlur={()=>animate(f1,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f2), backgroundColor:bg(f2)}]}>
              <TextInput
                placeholder="이메일 주소" placeholderTextColor={C[800]}
                keyboardType="email-address" autoCapitalize="none"
                value={email} onChangeText={setEmail}
                onFocus={()=>animate(f2,1)} onBlur={()=>animate(f2,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f3), backgroundColor:bg(f3)}]}>
              <TextInput
                placeholder="비밀번호 (8자 이상)" placeholderTextColor={C[800]} secureTextEntry
                value={pw} onChangeText={setPw}
                onFocus={()=>animate(f3,1)} onBlur={()=>animate(f3,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f4), backgroundColor:bg(f4)}]}>
              <TextInput
                placeholder="비밀번호 확인" placeholderTextColor={C[800]} secureTextEntry
                value={pw2} onChangeText={setPw2}
                onFocus={()=>animate(f4,1)} onBlur={()=>animate(f4,0)}
                style={styles.input}
              />
            </Animated.View>

            <Pressable
              style={[styles.primaryBtn, (!emailOK(email) || pw.length<8 || !name || !pw2 || loading) && { opacity:0.6 }]}
              disabled={!emailOK(email) || pw.length<8 || !name || !pw2 || loading}
              onPress={onSubmit}
            >
              {loading ? <ActivityIndicator /> : <Text style={styles.primaryText}>계속</Text>}
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:{ flex:1, backgroundColor:C.white },
  header:{ height:56, justifyContent:"center", alignItems:"center", marginTop:20 },
  headerTitle:{ fontSize:18, fontWeight:"600", color:C[900] },
  scrollInner:{ paddingBottom:24 },
  form:{ width:"90%", alignSelf:"center" },
  field:{ borderWidth:1, borderColor:C[200], borderRadius:14, backgroundColor:C.white, paddingHorizontal:14, marginBottom:12 },
  input:{ height:45, fontSize:16 },
  primaryBtn:{ height:52, borderRadius:14, borderWidth:1.5, borderColor:C[800], backgroundColor:C[600],
    alignItems:"center", justifyContent:"center", alignSelf:"center", width:"100%", marginTop:10 },
  primaryText:{ color:C.white, fontSize:16, fontWeight:"900" },
});
