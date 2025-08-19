// src/components/MessageBubble.tsx (살짝 개선)
import React from "react";
import { View, Text, TextStyle } from "react-native";
type Role = "user"|"assistant";

export default function MessageBubble({
  role, children, textStyle
}:{role:Role; children:React.ReactNode; textStyle?:TextStyle}){
  const isUser = role==="user";
  return (
    <View style={{alignSelf:isUser?"flex-end":"flex-start", maxWidth:"85%", marginVertical:6}}>
      <View style={{
        padding:12, borderRadius:18,
        backgroundColor: isUser ? "#ebe8ddff" : "#FEF0B8"
      }}>
        {typeof children === "string"
          ? <Text style={{fontWeight:"300"}}>{children}</Text>
          : children}
      </View>
    </View>
  );
}
