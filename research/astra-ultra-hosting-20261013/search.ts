import {writeFileSync} from 'node:fs';
import {bins,roles,plan,placement,allowed,census,validate,swap,move,source,sha}from './core';
const start=Date.now(),deadline=Math.min(start+120000,Date.parse('2026-10-13T23:40:30Z'));
if(Date.now()>=deadline)throw Error("Sprint search window expired; frozen verification remains available");
const before=census(),edits:any[]=[],stats={pairs:0,capacity:0,legal:0,improving:0};
function pairscan(){const partial=bins.filter(b=>b.free>0&&b.free<b.cap);for(let ai=0;ai<partial.length;ai++)for(let bi=ai+1;bi<partial.length;bi++){const a=partial[ai],b=partial[bi];for(const i of a.roles)for(const j of b.roles){stats.pairs++;let d=roles[i].width-roles[j].width,x=a.free,y=b.free;if(x+d<0||y-d<0)continue;stats.capacity++;if(Math.max(x+d,y-d)<=Math.max(x,y))continue;if(!allowed(i,b,[j])||!allowed(j,a,[i]))continue;stats.legal++;stats.improving++;edits.push({kind:'swap',i,j,from:[a.key,b.key],free_before:[x,y],free_after:[x+d,y-d]});swap(i,j);return true;}if(Date.now()>deadline)return false;}return false;}
while(pairscan()&&Date.now()<deadline){}
validate();const out={status:edits.length?'PROVISIONAL_LEGAL_OWNER_GAIN':'NO_PAIR_SWAP_GAIN',elapsed_ms:Date.now()-start,before,after:census(),stats,edits,pins:{owners:sha(source+'/data/OWNERS.json.gz'),plan:sha(source+'/data/PLAN.json')},scope:'Two distinct partially filled bins; two whole-role swaps; strict concentration sufficient for every 0<a<1. No full operator/invoice admission yet.'};
writeFileSync(import.meta.dir+'/SEARCH.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
