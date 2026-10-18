import{writeFileSync}from'node:fs';
import{bins,roles,placement,occupied,allowed,census,validate,move,source,sha}from'./core';
const start=Date.now(),deadline=Math.min(start+120000,Date.parse('2026-10-13T23:40:30Z'));
if(Date.now()>=deadline)throw Error("Sprint search window expired; frozen verification remains available");
const original=census(),edits:any[]=[],stats={roots:0,states:0,neutral_edges:0,terminal_tests:0};
// A width-7 move from a full bin into a free-rank-7 bin transfers the gap.
// Its only occupancy change relevant to the new gap is the deleted role's time.
const donors=roles.map((r,i)=>({r,i,b:bins[placement[i]]})).filter(x=>x.r.width===7&&x.b.free===0);
const terminals=roles.map((r,i)=>({r,i,b:bins[placement[i]]})).filter(x=>x.b.free>0&&x.b.free+x.r.width>7&&x.r.width<=7);
let found:any=null;
for(const root of bins.filter(b=>b.free===7)){
 stats.roots++;const queue=[{bin:root.id,freed:-1,parent:-1,role:-1,depth:0}],seen=new Set<string>([`${root.id},-1`]);
 for(let qi=0;qi<queue.length;qi++){
  if(Date.now()>deadline)break;const state=queue[qi],hole=bins[state.bin];stats.states++;
  const feasible=(i:number)=>hole.allowed.has(roles[i].time)&&(!occupied[roles[i].time].has(hole.family)||roles[i].time===state.freed);
  const pathBins=new Set<number>();let cur=qi;while(cur>=0){pathBins.add(queue[cur].bin);cur=queue[cur].parent}
  for(const {r,i,b}of terminals){stats.terminal_tests++;if(pathBins.has(b.id)||!feasible(i))continue;
   const sequence:any[]=[];cur=qi;while(queue[cur].parent>=0){const z=queue[cur];sequence.push({role:z.role,to:queue[z.parent].bin});cur=z.parent;}sequence.reverse();sequence.push({role:i,to:state.bin});
   found={root:root.key,depth:state.depth+1,sequence};break;
  }
  if(found)break;
  if(state.depth>=8)continue;
  for(const {r,i,b}of donors){if(pathBins.has(b.id)||!feasible(i))continue;const key=`${b.id},${r.time}`;if(seen.has(key))continue;seen.add(key);stats.neutral_edges++;queue.push({bin:b.id,freed:r.time,parent:qi,role:i,depth:state.depth+1});}
 }
 if(found||Date.now()>deadline)break;
}
if(found){for(const e of found.sequence){const from=bins[placement[e.role]],to=bins[e.to];edits.push({kind:'move',i:e.role,from:from.key,to:to.key,width:roles[e.role].width,free_before:[from.free,to.free]});move(e.role,to);}validate();}
const out={status:found?'PROVISIONAL_LEGAL_OWNER_GAIN':'NO_NEUTRAL_7_PATH_FOUND',elapsed_ms:Date.now()-start,before:original,after:census(),stats,found,edits,pins:{owners:sha(source+'/data/OWNERS.json.gz'),plan:sha(source+'/data/PLAN.json')},scope:'Width-7 hole transfers across full bins, at most 8 neutral moves, then one strictly improving relocation. BFS state pruning retains one path per (bin,freed-time); failed search not exhaustive over histories.'};
writeFileSync(import.meta.dir+'/NEUTRAL-SEARCH.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
