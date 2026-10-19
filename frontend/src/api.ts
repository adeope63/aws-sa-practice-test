export async function api<T>(path:string,body?:unknown,method?:string):Promise<T>{
 const r=await fetch('/api'+path,{method:method||(body===undefined?'GET':'POST'),headers:body===undefined?undefined:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
 const data=await r.json(); if(!r.ok) throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail)); return data;
}
export const percentage=(value:number|null|undefined)=>value==null?'—':`${Math.round(value)}%`;
export function selectAnswer(current:string[],id:string,count:number){return current.includes(id)?current.filter(x=>x!==id):count===1?[id]:current.length<count?[...current,id]:current;}
export function timeLabel(seconds:number){const s=Math.max(0,Math.floor(seconds)); return `${Math.floor(s/3600).toString().padStart(2,'0')}:${Math.floor(s%3600/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;}
