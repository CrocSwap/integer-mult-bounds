"""Transfer only the frozen19 beneficial frame changes to the independently rebuilt PR541 word.
The unconstrained minimum-frame composition is a retained losing experiment.
"""
from pathlib import Path
from collections import Counter
import json,gzip,copy,time
R=Path(__file__).resolve().parent;O=R/'trace541-frozen-minimum';O.mkdir(exist_ok=False)
a=json.load(gzip.open(R/'bit510-observable-slice/WORD.json.gz'));src=json.load(gzip.open(R/'trace541-observable-slice/WORD.json.gz'));low=json.load(gzip.open(R/'bit510-sliced-minimal-frames/WORD.json.gz'));moves=json.loads((R/'bit510-sliced-minimal-frames/RESULT.json').read_text())['moves'];w=copy.deepcopy(src);assert w['frames']==a['frames'];w['frames']=low['frames'];assert len(w['A'])-len(a['A'])==60
selected={}
for x in moves:
 assert x['section']=='A';i=x['index'];assert w['A'][i+60]==a['A'][i]
 selected[i+60]=x['new']
cur=list(w['start']);masks=[sum(1<<r for r in f)for f in w['frames']];accepted=[];rejected=[]
for i,(f,d,ss)in enumerate(w['A']):
 if i in selected:
  q=selected[i]
  if all(masks[cur[r]]&masks[q]==masks[cur[r]]for r in [d]+ss):f=q;w['A'][i][0]=f;accepted.append(i)
  else:rejected.append(i)
 for r in [d]+ss:assert masks[cur[r]]&masks[f]==masks[cur[r]];cur[r]=f
# Scalar word is unchanged from the already reconstructed PR541 slice; cleanup uses full frame1.
assert all(x[1:]==y[1:]for x,y in zip(w['A'],src['A']))
(O/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))
res=dict(status='PASS_FROZEN_FRAME_TRANSFER_CONTAINMENTS',accepted_indices=accepted,rejected_indices=rejected,scope='Only previously beneficial19 operation-frame changes transferred to sliced PR541 by exact gate identity; full scalar/geometry/profile/physical checks follow.')
(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)
