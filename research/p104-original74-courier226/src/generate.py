#!/usr/bin/env python3
"""Literal #7617 courier adapted to strict #7645; clocks are baseline zero-based."""
import gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
base=D/'baseline.json.gz'
w=json.loads(gzip.decompress(base.read_bytes())); raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(raw).hexdigest()=='6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
p=w['program']
removed={41470:['MOVE',226,260,719,False],41471:['ADD',473,226,'1',719],43516:['MOVE',226,719,907,False],43517:['ADD',166,226,'-1/2',907],45736:['MOVE',226,907,127,False],45739:['MOVE',990,907,127,False]}
insert={41466:[p[41470],p[41471],['ADD',990,226,'-1',719]],45738:[p[45739],['MOVE',226,719,127,False],['ADD',990,226,'1',127]]}
for i,e in removed.items():assert p[i]==e,(i,p[i],e)
assert p[41465]==['ADD',990,473,'-1',719] and p[41466]==['MOVE',990,719,907,False]
assert p[43515]==['ADD',166,990,'1/2',907] and p[45738]==['ADD',1477,226,'1',127]
assert p[45740]==['ADD',990,1477,'1',127]
out=[];align={};inserted=[]
for i,e in enumerate(p):
 for item in insert.get(i,[]):inserted.append({'before_source_clock':i,'candidate_clock':len(out),'event':item});out.append(item)
 if i not in removed:align[str(i)]=len(out);out.append(e)
w['program']=out;raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode(); digest=hashlib.sha256(raw).hexdigest()
(D/'candidate.json.gz').write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
manifest={'source_word_sha256':'6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf','source_head':'8ee7e6869b57ce445dbebd1d720366eab1f8ca40','courier_source_head':'12f6626e194808fa38f473a3e84b2f81e169e3d3','candidate_word_sha256':digest,'source_events':len(p),'candidate_events':len(out),'removed':[{'source_clock':i,'event':e} for i,e in removed.items()],'inserted':inserted,'aligned_origins':align}
(D/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ('source_word_sha256','candidate_word_sha256','source_events','candidate_events','removed','inserted')},indent=2))
