"""Independent common-frame incidence closure for each late nonzero cut line."""
import json,gzip
from pathlib import Path
p=Path(__file__).resolve().parent;r=p.parent;w=json.loads(gzip.decompress((p/'inputs/word-base.json.gz').read_bytes()));N=224+w['report']['R'];results=[]
seq=[('B',i,e)for i,e in enumerate(w['B'])]+[('tail',i,w['cleanup'][ci][:-1]+[U])for i,(ci,U)in enumerate(w['early_cleanup'])]
for k in range(8):
 normal=next(x for x in range(1,512)if all(not(x&z).bit_count()%2 for z in w['center_frames'][k]));record=dict(receivers=sorted({e[1]for e in w['cut']if e[2]==w['centers'][k]}));reached={i:dict(origin=i,path=[])for i in record['receivers']}
 for sec,idx,e in seq:
  regs=e[1:3]if e[0]=='add'else e[1:2];have=[i for i in regs if i in reached]
  if not have:continue
  donor=have[0]
  for i in regs:
   if i not in reached:reached[i]=dict(origin=reached[donor]['origin'],path=reached[donor]['path']+[dict(section=sec,index=idx,source=donor,target=i)])
 targets=[i for i in reached if 112<=i<224 and(normal&w['ports'][i-112]).bit_count()%2]
 helpers=[]
 for i in reached:
  if i<224:continue
  U=w['helper_final'].get(str(i),[1<<j for j in range(9)]);span={0}
  for x in U:span|={a^x for a in span}
  if normal not in span:helpers.append(i)
 results.append(dict(pivot=k,normal=normal,seed_receivers=record['receivers'],reached=len(reached),incompatible_targets=targets,incompatible_helpers=helpers,witnesses={str(i):reached[i]for i in targets+helpers}))
print([(x['pivot'],len(x['incompatible_targets']),len(x['incompatible_helpers']),x['reached'])for x in results])
out=dict(status='PASS_INDEPENDENT_COMMON_FRAME_REACHABILITY',results=results,scope='Closure under the retained B and early-tail incidences; necessary only for that common-frame chronology. Changed gates/order, zero-value exemptions, different endpoint contracts and new decoders are not excluded.')
assert out==json.loads((p/'CUT-REACHABILITY.json').read_text()),'reachability receipt mismatch'
print('PASS_RETAINED_SCATTER_OBSTRUCTION')
