import{readFileSync,writeFileSync}from'node:fs';import{gunzipSync}from'node:zlib';import{isDeepStrictEqual}from'node:util';
import{read,roles,plan,bins,bykey,placement,move,validate,census,source,sha,need}from'./core';
const p=import.meta.dir,c=read(p+'/CONSTRUCTION.json'),candidate=read(p+'/data/OWNERS.json.gz');
need(c.pins.owners===sha(source+'/data/OWNERS.json.gz')&&c.pins.plan===sha(source+'/data/PLAN.json'),'source pins');
const initial=census();let actions=0;
for(const round of c.rounds){const r=round.edits;for(let k=0;k<r.length;k++){const e=r[k],a=bins[placement[e.i]],b=bykey.get(e.to)!;need(a.key===e.from&&roles[e.i].width===e.width,'edit identity');const x=a.free,y=b.free,w=e.width;need(isDeepStrictEqual(e.free_before,[x,y]),'before state');if(k<r.length-1)need(x+w===y,'neutral step');else need(x+w>y,'strict concentration');move(e.i,b);actions++;}validate();need(isDeepStrictEqual(census(),round.after),'round census');}
need(isDeepStrictEqual(census(),c.after),'final census');
const realized=structuredClone(roles);for(const b of bins){let offset=0;for(const i of b.roles){Object.assign(realized[i],{owner_replica:b.rep,child:b.child,port:b.port,copy:b.rep*112+b.port,family:b.family,offset});offset+=roles[i].width;}}
need(isDeepStrictEqual(realized,candidate),'frozen literal candidate');
function check(raw:any[]){need(raw.length===roles.length,'role count');const seen=new Set(),cells=new Map<string,Set<number>>();for(let i=0;i<raw.length;i++){const r=raw[i],original=roles[i];for(const k of['time','stage','replica','helper','width'])need(r[k]===original[k],'changed identity');const key=`${r.owner_replica},${r.child},${r.port}`,b=bykey.get(key);need(b&&r.family===b.family&&r.copy===r.owner_replica*112+r.port,'bad family');need(b.allowed.has(r.time),'bad window');const ident=`${r.time},${r.family}`;need(!seen.has(ident),'alias');seen.add(ident);const used=cells.get(key)||new Set();for(let x=r.offset;x<r.offset+r.width;x++){need(Number.isInteger(x)&&x>=0&&x<b.cap&&!used.has(x),'bad cell');used.add(x)}cells.set(key,used);}const h:Record<string,number>={};for(const b of bins){const used=cells.get(b.key)||new Set();for(let x=0;x<used.size;x++)need(used.has(x),'not prefix');h[b.cap-used.size]=(h[b.cap-used.size]||0)+1;}return h;}
need(isDeepStrictEqual(check(roles),initial),'baseline positive control');need(isDeepStrictEqual(check(candidate),c.after),'literal candidate owner check');
const controls:string[]=[];
for(const[name,mutate]of [
 ['omit_first_neutral',(a:any[])=>{const i=c.rounds[0].edits[0].i;a[i]=structuredClone(roles[i])}],
 ['wrong_family',(a:any[])=>a[0].family++],
 ['changed_width',(a:any[])=>a[0].width++],
 ['overlapping_offset',(a:any[])=>{const b=bins.find(b=>b.roles.length>1)!;a[b.roles[1]].offset=a[b.roles[0]].offset}],
 ['after_deadline',(a:any[])=>{const i=0,r=a[i];const b=bins.find(b=>b.cap>=r.width&&!b.allowed.has(r.time))!;Object.assign(r,{owner_replica:b.rep,child:b.child,port:b.port,copy:b.rep*112+b.port,family:b.family,offset:0})}],
]as const){const a=structuredClone(candidate);mutate(a);let rejected=false;try{check(a)}catch{rejected=true}need(rejected,'control accepted '+name);controls.push(name)}
const out={status:'PASS_EXACT_COMPOUND_OWNER_CONSTRUCTION',roles:roles.length,bins:bins.length,rounds:c.rounds.length,actions,changed_serialized_rows:c.changed_rows,baseline:initial,candidate:c.after,profile:c.profile,exponent_uniform_gain:'Each strict final move sends free ranks (x,y) to (x+w,y-w), with 0<=y-w and x+w>y, hence strictly increases concentration. r^(1-a) is strictly concave for 0<a<1.',controls_rejected:controls,scope:'Exact finite owner construction and strict moment improvement; native source-bound operator, invoice, and outer acceptance are separate receipts.'};
writeFileSync(p+'/OWNER-CHECK.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
