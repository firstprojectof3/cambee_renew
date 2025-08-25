import React, { useRef, useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable, Image, Animated, Easing,
         KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { login } from "../services/api"; // 경로 맞게
import { saveUser } from "../state/auth";


const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};


export default function AuthScreen({ navigation }: any){
  const [remember, setRemember] = useState(false);
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string|null>(null);
  const fEmail = useRef(new Animated.Value(0)).current;
  const fPw = useRef(new Animated.Value(0)).current;

  const animate = (v: Animated.Value, to: 0|1) =>
    Animated.timing(v,{ toValue:to, duration:180, easing:Easing.out(Easing.quad), useNativeDriver:false}).start();

  const emailBorder = fEmail.interpolate({ inputRange:[0,1], outputRange:[C[950], C[600]] });
  const emailBg     = fEmail.interpolate({ inputRange:[0,1], outputRange:[C.white, C[50]] });
  const pwBorder    = fPw.interpolate({ inputRange:[0,1],  outputRange:[C[950], C[600]] });
  const pwBg        = fPw.interpolate({ inputRange:[0,1],  outputRange:[C.white, C[50]] });

  return (
    <View style={styles.container}>
      {/* 전체 배경 그라데이션: 0% 흰 → 70% 연노랑 → 90% 진노랑 → 100% 더 진 */}
      <LinearGradient
        colors={[C.white, C[100], C[300], C[500]]}
        locations={[0, 0.7, 0.9, 1]}
        start={{ x:0.5, y:1 }}
        end={{ x:0.5, y:0 }}
        style={StyleSheet.absoluteFill}
      />

      {err ? <Text style={{ color:"crimson", textAlign:"center", marginBottom:8 }}>{err}</Text> : null}

      <KeyboardAvoidingView behavior={Platform.select({ ios:"padding", android:undefined })} style={styles.wrap}>
        {/* 상단 히어로: 로고 가운데 + 앱명 + 짧은 카피 */}
        <View style={styles.hero}>
          <Image source={require("../../assets/app_logo.png")} style={styles.logo} resizeMode="contain" />
          
          <Text style={styles.heroCopy}>캠퍼스 정보 궁금할 땐,</Text>
          <Text style={styles.heroTitle}>CAMBEE</Text>
        </View>

        {/* 하단 폼 영역 */}
        <View style={styles.form}>
          <Animated.View style={[styles.field, { borderColor: emailBorder, backgroundColor: emailBg }]}>
            <TextInput
              placeholder="이메일 주소"
              placeholderTextColor={C[800]}
              keyboardType="email-address"
              autoCapitalize="none"
              value={email}
              onChangeText={setEmail}
              onFocus={()=>animate(fEmail,1)}
              onBlur={()=>animate(fEmail,0)}
              style={styles.input}
            />
          </Animated.View>

          <Animated.View style={[styles.field, { borderColor: pwBorder, backgroundColor: pwBg }]}>
            <TextInput
              placeholder="비밀번호"
              placeholderTextColor={C[800]}
              secureTextEntry
              value={pw}
              onChangeText={setPw}
              onFocus={()=>animate(fPw,1)}
              onBlur={()=>animate(fPw,0)}
              style={styles.input}
            />
          </Animated.View>

          <View style={styles.helperRow}>
            <Pressable onPress={()=>setRemember(!remember)} style={styles.checkRow}>
              <View style={[styles.checkbox, remember && { backgroundColor:C[500], borderColor:C[950] }]} />
              <Text style={styles.helperText}>30일 동안 기억해요</Text>
            </Pressable>
            <Pressable onPress={()=>{ /* TODO: route */ }}>
              <Text style={[styles.helperText, styles.linkText]}>비밀번호 찾기</Text>
            </Pressable>
          </View>

          <Pressable 
            style={[
              styles.primaryBtn,
              (!email.includes("@") || pw.length < 4 || loading) && { opacity:0.6 }
            ]}
            disabled={!email.includes("@") || pw.length < 4 || loading}
            onPress={async ()=>{
              if (loading) return;
              setErr(null);
              setLoading(true);
              try{
                const res = await login({ email, password: pw });
                console.log("✅ login ok:", res);
                await saveUser(res.user);
                navigation.replace("Home");
              }catch(e:any){
                console.log("❌ login err:", e.message);
                setErr("로그인 실패");
              }finally{
                setLoading(false);
              }
            }}
            accessibilityLabel="로그인"
          >
            {loading ? <ActivityIndicator /> : <Text style={styles.primaryText}>로그인</Text>}
          </Pressable>

          <View style={styles.bottomNote}>
            <Text style={styles.noteText}>계정이 없으신가요? </Text>
            <Pressable onPress={()=>navigation.navigate("Register1")}>
              <Text style={[styles.noteText, styles.linkText]}>회원가입</Text>
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container:{ flex:1  },
  wrap:{ flex:1 , justifyContent:"space-between", paddingHorizontal:16, paddingTop:24 },

  hero:{ alignItems:"center", justifyContent:"center", paddingTop:12 },
  logo:{ width:180, height:180, marginTop:60  },
  heroTitle:{ fontSize:36, fontWeight:"700", color:C[800], letterSpacing:1.7 },
  heroCopy:{ marginTop:6, fontSize:17, color:C[700], textAlign:"center", width:"90%" },

  form:{ width:"90%", alignSelf:"center", paddingBottom:6 },
  field:{ borderWidth:1.6, borderColor:C[950], borderRadius:14, backgroundColor:C.white, paddingHorizontal:14, marginBottom:14 },
  input:{ height:52, fontSize:16 },

  helperRow:{ flexDirection:"row", justifyContent:"space-between", alignItems:"center", marginTop:2, marginBottom:12 },
  checkRow:{ flexDirection:"row", alignItems:"center" },
  checkbox:{ width:18, height:18, borderWidth:1, borderColor:C[950], borderRadius:4, marginLeft:5, marginRight:8, backgroundColor:C.white },
  helperText:{ fontSize:13, color:C[900] },
  linkText:{ textDecorationLine:"underline", fontWeight:"800" },

  primaryBtn:{ height:52, borderRadius:14, borderWidth:1.5, borderColor:C[700], backgroundColor:C[600], alignItems:"center", justifyContent:"center", alignSelf:"center", width:"90%", marginTop:6 },
  primaryText:{ color:C.white, fontSize:16, fontWeight:"900" },

  bottomNote:{ flexDirection:"row", justifyContent:"center", alignItems:"center", marginTop:12, marginBottom:24
  },
  noteText:{ fontSize:14, color:C[900] },
});

