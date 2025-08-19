// src/screens/register.tsx
import React, { useRef, useState } from "react";
import {
  View, Text, StyleSheet, TextInput, Pressable, Image,
  Animated, Easing, KeyboardAvoidingView, Platform, Alert, ScrollView
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";

const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};

export default function RegisterScreen({ navigation }: any){
  // form state
  const [name, setName] = useState("");
  const [email,setEmail] = useState("");
  const [pw,setPw] = useState("");
  const [pw2,setPw2] = useState("");
  const [school,setSchool] = useState("");
  const [dept,setDept] = useState("");
  const [grade,setGrade] = useState("");
  const [sid,setSid] = useState("");

  // focus anims (얇은 라인 + 연한 배경)
  const makeAV = () => useRef(new Animated.Value(0)).current;
  const f1=makeAV(), f2=makeAV(), f3=makeAV(), f4=makeAV(), f5=makeAV(), f6=makeAV(), f7=makeAV(), f8=makeAV();
  const animate = (v: Animated.Value, to: 0|1) =>
    Animated.timing(v,{ toValue:to, duration:160, easing:Easing.out(Easing.quad), useNativeDriver:false }).start();
  const b = (v: Animated.Value)=>v.interpolate({ inputRange:[0,1], outputRange:[C[200], C[500]] });
  const bg= (v: Animated.Value)=>v.interpolate({ inputRange:[0,1], outputRange:[C.white, C[50]] });

  const onSubmit = () => {
    if(!name||!email||!pw||!pw2||!school||!dept||!grade||!sid){
      return Alert.alert("알림","모든 항목을 입력해 주세요.");
    }
    if(pw !== pw2){
      return Alert.alert("알림","비밀번호가 일치하지 않습니다.");
    }
    Alert.alert("완료","회원가입이 성공적으로 되었습니다. 홈으로 이동합니다.",[
      { text:"확인", onPress:()=>navigation.replace("Home") }
    ]);
  };

  return (
    <View style={styles.container}>
      {/* 연한 노랑만, 방향 반대로(위→아래 옅어짐) */}
      <LinearGradient
        colors={[C[50], C[100], C[50]]}
        locations={[0, 0.6, 1]}
        start={{ x:0.5, y:0 }}
        end={{ x:0.5, y:1 }}
        style={StyleSheet.absoluteFill}
      />

      <KeyboardAvoidingView behavior={Platform.select({ ios:"padding", android:undefined })} style={{flex:1}}>
        {/* 헤더: 좌상단 뒤로가기 / 중앙 타이틀 */}
        <View style={styles.header}>
          <Pressable onPress={()=>navigation.goBack()} hitSlop={12} style={styles.backBtn}>
            <Text style={styles.backTxt}>←</Text>
          </Pressable>
          <Text style={styles.headerTitle}>회원가입</Text>
        </View>

        {/* 안내 카피 */}
        <View style={styles.copyBox}>
          <Text style={styles.copyMain}>Cambee에 오신 걸 환영해요.</Text>
          <Text style={styles.copySub}>원활한 사용을 위해 다음 정보를 입력해 주세요.</Text>
        </View>

        <ScrollView
          contentContainerStyle={styles.scrollInner}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
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
                placeholder="비밀번호" placeholderTextColor={C[800]} secureTextEntry
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

            <Animated.View style={[styles.field,{ borderColor:b(f5), backgroundColor:bg(f5)}]}>
              <TextInput
                placeholder="학교 이름" placeholderTextColor={C[800]}
                value={school} onChangeText={setSchool}
                onFocus={()=>animate(f5,1)} onBlur={()=>animate(f5,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f6), backgroundColor:bg(f6)}]}>
              <TextInput
                placeholder="학과 이름" placeholderTextColor={C[800]}
                value={dept} onChangeText={setDept}
                onFocus={()=>animate(f6,1)} onBlur={()=>animate(f6,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f7), backgroundColor:bg(f7)}]}>
              <TextInput
                placeholder="학년(숫자)" placeholderTextColor={C[800]}
                keyboardType="number-pad"
                value={grade} onChangeText={setGrade}
                onFocus={()=>animate(f7,1)} onBlur={()=>animate(f7,0)}
                style={styles.input}
              />
            </Animated.View>

            <Animated.View style={[styles.field,{ borderColor:b(f8), backgroundColor:bg(f8)}]}>
              <TextInput
                placeholder="학번(숫자)" placeholderTextColor={C[800]}
                keyboardType="number-pad"
                value={sid} onChangeText={setSid}
                onFocus={()=>animate(f8,1)} onBlur={()=>animate(f8,0)}
                style={styles.input}
              />
            </Animated.View>

            <Pressable style={styles.primaryBtn} onPress={onSubmit} accessibilityLabel="회원가입">
              <Text style={styles.primaryText}>회원가입</Text>
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:{ flex:1, backgroundColor:C.white },

  header:{ height:56, justifyContent:"center", alignItems:"center",marginTop:20 },
  backBtn:{ position:"absolute", left:16, padding:4 },
  backTxt:{ fontSize:22, fontWeight:"700", color:C[900] },
  headerTitle:{ fontSize:18, fontWeight:"600", color:C[900] },

  copyBox:{ width:"90%", alignSelf:"center", marginTop:20, marginBottom:30},
  copyMain:{ fontSize:22, fontWeight:"800", color:C[800] },
  copySub:{ marginTop:4, fontSize:16, color:C[700] },

  scrollInner:{ paddingBottom:24 },
  form:{ width:"90%", alignSelf:"center" },

  field:{
    borderWidth:1,              // 얇게
    borderColor:C[200],         // 연하게
    borderRadius:14,
    backgroundColor:C.white,
    paddingHorizontal:14,
    marginBottom:12
  },
  input:{ height:45, fontSize:16 },

  primaryBtn:{
    height:52, borderRadius:14, borderWidth:1.5, borderColor:C[800],
    backgroundColor:C[600],
    alignItems:"center", justifyContent:"center",
    alignSelf:"center", width:"100%", marginTop:10
  },
  primaryText:{ color:C.white, fontSize:16, fontWeight:"900" },
});
