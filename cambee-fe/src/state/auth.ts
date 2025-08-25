// src/state/auth.ts
import * as SecureStore from "expo-secure-store";
export const saveUser = (u:any)=>SecureStore.setItemAsync("user", JSON.stringify(u));
export const loadUser = async()=>JSON.parse(await SecureStore.getItemAsync("user")||"null");
export const clearUser = ()=>SecureStore.deleteItemAsync("user");

