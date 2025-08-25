// src/components/ProfileCard.tsx
import { View, Text, StyleSheet, Pressable, Image } from "react-native";

const C={50:"#FFFAE6",100:"#FEF0B8",200:"#FEE685",300:"#FDDD5D",400:"#FDD430",500:"#FCCA03",600:"#CFA602",700:"#A28202",800:"#745D01",900:"#473901",950:"#191400",white:"#FFFFFF"};

type User = { name:string; school:string; major:string; grade:number; student_number:number };
type Props = { user: User; onEdit?:()=>void };

export default function ProfileCard({ user, onEdit }: Props){
  return (
    <View style={s.card}>
      {/* 상단 아바타 + 이름 + 편집 버튼 */}
      <View style={s.headerRow}>
        <Image source={{uri:"https://via.placeholder.com/64"}} style={s.avatar}/>
        <View style={{flex:1}}>
          <Text style={s.name}>{user.name}</Text>
          <Text style={s.sub}>학번 {user.student_number}</Text>
        </View>
          <Pressable onPress={onEdit} style={s.editBtn}>
            <Text style={s.editTxt}>편집</Text>
          </Pressable>
      </View>

      {/* 정보 리스트 */}
      <View style={s.row}><Text style={s.k}>학교</Text><Text style={s.v}>{user.school}</Text></View>
      <View style={s.row}><Text style={s.k}>학과</Text><Text style={s.v}>{user.major}</Text></View>
      <View style={s.row}><Text style={s.k}>학년</Text><Text style={s.v}>{user.grade}학년</Text></View>
    </View>
  );
}

const s=StyleSheet.create({
  card:{ padding:16, borderRadius:16, backgroundColor:C.white, borderWidth:1, borderColor:C[700], shadowColor:C[950], shadowOpacity:0.08, shadowRadius:8, elevation:2 },
  headerRow:{ flexDirection:"row", alignItems:"center", marginBottom:12 },
  avatar:{ width:60, height:60, borderRadius:28, margin:12, backgroundColor:C[100], borderWidth:1, borderColor:C[300] },
  name:{ margin:5, fontSize:25, fontWeight:"900", color:C[950] },
  sub:{ margin:2, fontSize:13, color:C[700] },

  row:{ flexDirection:"row", justifyContent:"space-between", marginVertical:7 },
  k:{ marginLeft: 15, fontSize:16, color:C[900] },
  v:{ marginRight: 10, fontSize:16, fontWeight:"800", color:C[700] },

  editBtn:{ paddingVertical:12, paddingHorizontal:12, margin:12, borderRadius:10, backgroundColor:C[400] },
  editTxt:{ fontSize:12, fontWeight:"800", color:C.white }
});

