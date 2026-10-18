import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
export const source='research/complex-t16-rare-pattern-exchanges';
export const read=(p:string)=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(p)).toString():readFileSync(p,'utf8'));
export const sha=(p:string)=>createHash('sha256').update(readFileSync(p)).digest('hex');
export const need=(x:any,msg:string)=>{if(!x)throw Error(msg)};
export const plan=read(source+'/data/PLAN.json');
export const roles:any[]=read(source+'/data/OWNERS.json.gz');
export type Bin={id:number,key:string,rep:number,child:number,port:number,family:number,cap:number,free:number,allowed:Set<number>,roles:number[]};
export const bins:Bin[]=[];export const bykey=new Map<string,Bin>();
for (const [key,[cap,times]]of Object.entries(plan.windows)as any){const[rep,child]=key.split(',').map(Number);for(let port=0;port<112;port++){
 const b={id:bins.length,key:`${rep},${child},${port}`,rep,child,port,family:rep*896+(2*plan.pairs[child]+plan.sides[child])*112+port,cap,free:cap,allowed:new Set<number>(times),roles:[]};bins.push(b);bykey.set(b.key,b);
}}
export const placement=roles.map((r,i)=>{const b=bykey.get(`${r.owner_replica},${r.child},${r.port}`)!;need(b&&r.family===b.family,'family');b.roles.push(i);b.free-=r.width;return b.id});
export const occupied=Array.from({length:144},()=>new Set<number>());
for(const r of roles){need(!occupied[r.time].has(r.family),'duplicate source family');occupied[r.time].add(r.family)}
export function allowed(i:number,b:Bin,removing:number[]=[]){const r=roles[i];return b.allowed.has(r.time)&&(!occupied[r.time].has(b.family)||removing.some(j=>roles[j].time===r.time&&bins[placement[j]].family===b.family));}
export function census(){const h:Record<string,number>={};for(const b of bins)h[b.free]=(h[b.free]||0)+1;return h}
export function validate(){let n=0;const occ=new Set<string>();for(const b of bins){let width=0;for(const i of b.roles){const r=roles[i];need(placement[i]===b.id,'placement');need(b.allowed.has(r.time),'window');need(!occ.has(`${r.time},${b.family}`),'alias');occ.add(`${r.time},${b.family}`);width+=r.width;n++}need(width+b.free===b.cap&&b.free>=0,'capacity')}need(n===roles.length,'role conservation');}
validate();
export function move(i:number,to:Bin){const from=bins[placement[i]],r=roles[i];need(to.free>=r.width&&allowed(i,to),'illegal move');from.roles.splice(from.roles.indexOf(i),1);to.roles.push(i);from.free+=r.width;to.free-=r.width;occupied[r.time].delete(from.family);occupied[r.time].add(to.family);placement[i]=to.id;}
export function swap(i:number,j:number){const a=bins[placement[i]],b=bins[placement[j]],ri=roles[i],rj=roles[j];const d=ri.width-rj.width;need(a.id!==b.id&&a.free+d>=0&&b.free-d>=0&&allowed(i,b,[j])&&allowed(j,a,[i]),'illegal swap');a.roles[a.roles.indexOf(i)]=j;b.roles[b.roles.indexOf(j)]=i;a.free+=d;b.free-=d;occupied[ri.time].delete(a.family);occupied[rj.time].delete(b.family);occupied[ri.time].add(b.family);occupied[rj.time].add(a.family);placement[i]=b.id;placement[j]=a.id;}
