// App.tsx
import React, { useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import * as SplashScreen from "expo-splash-screen";
import { useFonts } from "expo-font";
import { Text } from "react-native";
import { loadUser } from "./src/state/auth";
import { createNavigationContainerRef } from "@react-navigation/native";
import { Register1Screen, Register2Screen, OnboardingScreen, AuthScreen, HomeScreen, ChatScreen, SetupScreen } from "./src/screens";

export const navRef = createNavigationContainerRef();
SplashScreen.preventAutoHideAsync();
const Stack = createNativeStackNavigator();

export default function App() {
  const [fontsloaded] = useFonts({
    Pretendard: require("./assets/fonts/InterVariable.ttf"),
  });

  useEffect(() => {
    (async () => {
      if (!fontsloaded) return;
      (Text as any).defaultProps = (Text as any).defaultProps || {};
      (Text as any).defaultProps.style = { fontFamily: "Inter" };

      // ✅ 자동 로그인
      const u = await loadUser();
      if (u && navRef.isReady()) {
        navRef.reset({ index: 0, routes: [{ name: "Home" }] });
      }
      await SplashScreen.hideAsync();
    })();
  }, [fontsloaded]);

  return (
    <NavigationContainer ref={navRef}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Onboarding" component={OnboardingScreen} />
        <Stack.Screen name="Auth" component={AuthScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Chat" component={ChatScreen} />
        <Stack.Screen name="Register1" component={Register1Screen} />
        <Stack.Screen name="Register2" component={Register2Screen} />
        <Stack.Screen name="Setup" component={SetupScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
