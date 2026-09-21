import React,{createContext,useCallback,useContext,useEffect,useState}from'react';import{api}from'../services/api';
const AuthContext=createContext(null);
export function AuthProvider({children}){const[user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('savour_staff_user'))}catch{return null}});const[ready,setReady]=useState(false);
const clear=useCallback(()=>{localStorage.removeItem('savour_staff_token');localStorage.removeItem('savour_staff_user');setUser(null)},[]);
useEffect(()=>{const token=localStorage.getItem('savour_staff_token');if(!token){setReady(true);return}api.get('auth/me/').then(r=>{setUser(r.data);localStorage.setItem('savour_staff_user',JSON.stringify(r.data))}).catch(clear).finally(()=>setReady(true));const changed=()=>clear();window.addEventListener('savour-auth-changed',changed);return()=>window.removeEventListener('savour-auth-changed',changed)},[clear]);
const login=async(username,password)=>{const{data}=await api.post('auth/login/',{username,password});localStorage.setItem('savour_staff_token',data.token);localStorage.setItem('savour_staff_user',JSON.stringify(data.user));setUser(data.user);return data.user};
const logout=async()=>{try{await api.post('auth/logout/')}finally{clear()}};
return <AuthContext.Provider value={{user,ready,login,logout}}>{children}</AuthContext.Provider>}
export const useAuth=()=>useContext(AuthContext);
