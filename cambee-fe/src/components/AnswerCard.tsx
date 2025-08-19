// src/components/AnswerCard.tsx
import { View, Text, Pressable, Linking } from "react-native";
import { Answer } from "../types/chat";
export default function AnswerCard({ a }: { a: Answer }){
  return (
    <View style={{padding:14,borderRadius:16,backgroundColor:"#fff",borderWidth:1,borderColor:"#806a15ff"}}>
      <Text style={{fontSize:16,fontWeight:"700"}}>{a.title}</Text>
      <Text style={{marginTop:6,fontWeight:"500",color:"#CFA602"}}>{a.summary}</Text>
      <Text style={{marginTop:6,lineHeight:20,color:"#967f23ff"}} numberOfLines={3}>{a.content}</Text>
      <Pressable onPress={()=>Linking.openURL(a.link)}><Text style={{marginTop:4,textDecorationLine:"underline",fontWeight:"700",color:"#8b8981ff"}}>바로가기 ↗</Text></Pressable>
    </View>
  );
}
