"""Source-bound transfer of PR440 frame-only retimings to signed kernel75.
PR440 eumemic/OpenAI Codex; inherited PR436 eumemic/Claude, Apache-2.0.
Nomination and local geometry only; full signed finite invoice remains required.
"""
from pathlib import Path
import copy,hashlib,json,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
B=ROOT/'experiments/stage-search/pr436-integer-kernel';S=ROOT/'experiments/stage-search/pr440-source/stages'
canon=lambda w:json.dumps(w,sort_keys=True,separators=(',',':')).encode()
sha=lambda w:hashlib.sha256(canon(w)).hexdigest()
b=json.loads((B/'word.json').read_bytes()); f=json.loads((S/'final-word.json').read_bytes());r=json.loads((S/'retime-selection.json').read_bytes());sel=json.loads((B/'selected75/SELECTION.json').read_bytes())
assert sha(b)=='d6ec8811541d6ab59a3bbbaaa15bccc8918b3b43b23d9f593198cfe90826fd20'
assert sha(f)==r['output_sha256']=='bae58f0692326f180ba49642360fd55557f59a93a96a8fa62bf7babd55d2384e'
q=copy.deepcopy(b)
for ph in ('A','B','C'):q[ph]=[[fr,d,[x]]for fr,d,ss in q[ph]for x in ss]
offset=len(f['A'])-len(q['A']);assert offset==277
assert [g[1:]for g in f['A'][offset:]]==[g[1:]for g in q['A']]
frame_map={tuple(sorted(x)):i for i,x in enumerate(q['frames'])};changes=[]
for ph,i,old,new in r['gates']:
 assert ph=='A';j=i-offset;assert j>=0
 fr,d,ss=q['A'][j];assert tuple(sorted(q['frames'][fr]))==tuple(sorted(old))
 nf=frame_map[tuple(sorted(new))];assert f['A'][i]==[nf,d,ss]
 q['A'][j][0]=nf;changes.append(dict(baseline_index=j,old_frame=fr,new_frame=nf,destination=d,sources=ss))
assert len(changes)==57
raw=canon(q);(P/'baseline.json').write_bytes(raw)
s=copy.deepcopy(sel);s['source_sha256']=hashlib.sha256(raw).hexdigest()
# Construct parity word with exact sign-aware relation selection, retaining source role indices.
from collections import defaultdict
by=defaultdict(list);w=copy.deepcopy(q)
for z in s['entries']:
 p,fr=z['pivot'],z['frame'];w['start'][p]=fr
 for d,a in z['donor_coefficients']:by[d,fr].append(p)
pivs={z['pivot']for z in s['entries']}
w['D']=[[fr,d,[x for x in ss if x not in pivs]]for fr,d,ss in w['D']]
w['A']=[[fr,d,sorted(ps)]for(d,fr),ps in sorted(by.items())]+w['A'];w['C']+=[[q['final'][0],d,sorted(ps)]for(d,fr),ps in sorted(by.items())]
s['output_sha256']=sha(w);(P/'SELECTION.json').write_bytes(canon(s));(P/'word.json').write_bytes(canon(w))
report=dict(status='FRAME_RETIMITING_TRANSFER_NOMINATION_REQUIRES_ADMISSION',source_sha256=sha(b),retime_selection_sha256=hashlib.sha256((S/'retime-selection.json').read_bytes()).hexdigest(),baseline_sha256=sha(q),candidate_sha256=sha(w),moves=changes,source='https://github.com/CrocSwap/integer-mult-bounds/pull/440',head='bd03373b6d4d4e380d0b6ea7d55cd2ac8f163544')
(P/'TRANSFER.json').write_bytes(canon(report));print(report['candidate_sha256'])
