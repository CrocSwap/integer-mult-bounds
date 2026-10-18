import{writeFileSync,mkdirSync}from'node:fs';import{gzipSync}from'node:zlib';
import{bins,roles,placement,occupied,census,validate,move,source,sha,plan}from'./core';
const start=Date.now(),deadline=Math.min(start+90000,Date.parse('2026-10-13T23:39:00Z')),before=census(),rounds:any[]=[],allEdits:any[]=[];
if(Date.now()>=deadline)throw Error("Sprint search window expired; frozen verification remains available");
const stats={roots:0,states:0,edges:0,rounds:0};
for(let round=0;round<40&&Date.now()<deadline;round++){
 let found:any=null;const ranks=[...new Set(bins.filter(b=>b.free>0&&b.free<b.cap).map(b=>b.free))].sort((a,b)=>b-a);
 for(const rank of ranks){
  const donors=roles.map((r,i)=>({r,i,b:bins[placement[i]]})).filter(x=>x.b.free+x.r.width===rank);
  const terminals=roles.map((r,i)=>({r,i,b:bins[placement[i]]})).filter(x=>x.b.free>0&&x.b.free+x.r.width>rank&&x.r.width<=rank);
  if(!terminals.length)continue;
  for(const root of bins.filter(b=>b.free===rank&&b.roles.length)){
   stats.roots++;const queue=[{bin:root.id,freed:-1,parent:-1,role:-1,depth:0}],seen=new Set<string>([`${root.id},-1`]);
   for(let qi=0;qi<queue.length&&Date.now()<deadline;qi++){
    const state=queue[qi],hole=bins[state.bin];stats.states++;const feasible=(i:number)=>hole.allowed.has(roles[i].time)&&(!occupied[roles[i].time].has(hole.family)||roles[i].time===state.freed);
    const pathBins=new Set<number>();let cur=qi;while(cur>=0){pathBins.add(queue[cur].bin);cur=queue[cur].parent}
    for(const {r,i,b}of terminals){if(pathBins.has(b.id)||!feasible(i))continue;const seq:any[]=[];cur=qi;while(queue[cur].parent>=0){const z=queue[cur];seq.push({role:z.role,to:queue[z.parent].bin});cur=z.parent;}seq.reverse();seq.push({role:i,to:state.bin});found={root:root.key,rank,sequence:seq};break;}
    if(found)break;if(state.depth>=6)continue;
    for(const{r,i,b}of donors){if(pathBins.has(b.id)||!feasible(i))continue;const key=`${b.id},${r.time}`;if(seen.has(key))continue;seen.add(key);stats.edges++;queue.push({bin:b.id,freed:r.time,parent:qi,role:i,depth:state.depth+1});}
   }
   if(found||Date.now()>deadline)break;
  }
  if(found||Date.now()>deadline)break;
 }
 if(!found)break;
 const edits:any[]=[];for(const e of found.sequence){const from=bins[placement[e.role]],to=bins[e.to];edits.push({i:e.role,from:from.key,to:to.key,width:roles[e.role].width,free_before:[from.free,to.free]});move(e.role,to);}validate();rounds.push({...found,edits,after:census()});allEdits.push(...edits);stats.rounds++;console.log(JSON.stringify({round,depth:edits.length,after:census()}));
}
validate();const result=structuredClone(roles);for(const b of bins){let offset=0;for(const i of b.roles){Object.assign(result[i],{owner_replica:b.rep,child:b.child,port:b.port,copy:b.rep*112+b.port,family:b.family,offset});offset+=roles[i].width;}}
const after=census(),profile={...plan.profile};for(const[r,n]of Object.entries(before)){if(+r)profile[r]=(profile[r]||0)-n}for(const[r,n]of Object.entries(after)){if(+r)profile[r]=(profile[r]||0)+n}for(const r in profile)if(!profile[r])delete profile[r];
const out={status:rounds.length?'PROVISIONAL_LEGAL_OWNER_GAIN':'NO_GAIN',elapsed_ms:Date.now()-start,before,after,stats,rounds,profile,changed_rows:result.filter((r,i)=>JSON.stringify(r)!==JSON.stringify(roles[i])).length,pins:{owners:sha(source+'/data/OWNERS.json.gz'),plan:sha(source+'/data/PLAN.json')},scope:'Neutral same-rank residual transfers, depth <=6, followed by one strict concentration. 40 rounds / 90 seconds cap. Exact move legality on final emitted owner map; no universal failed-search claim.'};
mkdirSync(import.meta.dir+'/data',{recursive:true});writeFileSync(import.meta.dir+'/data/OWNERS.json.gz',gzipSync(JSON.stringify(result),{level:9}));writeFileSync(import.meta.dir+'/CONSTRUCTION.json',JSON.stringify(out,null,2)+'\n');writeFileSync(import.meta.dir+'/data/PROFILE.json',JSON.stringify(profile,null,2)+'\n');console.log(JSON.stringify({status:out.status,elapsed_ms:out.elapsed_ms,stats,after,profile,changed_rows:out.changed_rows}));
