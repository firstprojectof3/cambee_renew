// src/screens/onboarding.tsx
import { useEffect, useRef } from "react";
import { View, Text, Image, StyleSheet, Animated, Easing } from "react-native";
import { LinearGradient } from "expo-linear-gradient";

const C = {
  50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",
  500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"
};

export default function OnboardingScreen({ navigation }: any) {
  const fade = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const D_IN = 800, D_HOLD = 3400, D_OUT = 800, TOTAL = D_IN + D_HOLD + D_OUT; // 5000ms
    Animated.sequence([
      Animated.timing(fade, { toValue: 1, duration: D_IN, easing: Easing.out(Easing.quad), useNativeDriver: true }),
      Animated.delay(D_HOLD),
      Animated.timing(fade, { toValue: 0, duration: D_OUT, easing: Easing.in(Easing.quad), useNativeDriver: true }),
    ]).start();
    const t = setTimeout(() => navigation.replace("Auth"), TOTAL);
    return () => clearTimeout(t);
  }, [fade, navigation]);

  return (
    <View style={styles.container} pointerEvents="none">
      {/* 바텀 50% 그라데이션: 아래 진함 → 위로 옅어짐 */}
      <LinearGradient
        colors={[C[200], C[100], C[50] + "00"]}
        start={{ x: 0.5, y: 1 }}
        end={{ x: 0.5, y: 0 }}
        style={styles.bottomGlow}
      />
      <Animated.View style={[styles.center, { opacity: fade }]}>
        <Image source={require("../../assets/app_logo.png")} style={styles.logo} resizeMode="contain" />
        <Text style={styles.brand}>CAMBEE</Text>
        <Text style={styles.copy}>© 2025 Cambee Team. All rights reserved.</Text>
        
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.white, alignItems: "center", justifyContent: "center" },
  center: { alignItems: "center" },
  bottomGlow: { position: "absolute", left: 0, right: 0, bottom: 0, height: "50%" },
  logo: { width: 250, height: 250, marginBottom: 12 }, // ⬅️ 크게
  copy: { fontSize: 12, color: C[700], marginBottom: 6, letterSpacing: 0.2 },
  brand: { fontSize: 40, fontWeight: "700", color: C[800], letterSpacing: 0.6 },
});
