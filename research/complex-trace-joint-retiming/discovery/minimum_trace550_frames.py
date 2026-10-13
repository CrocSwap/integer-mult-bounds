"""Causal minimum-frame screen after PR550's scalar source substitution.
Fixed scalar word, entrances and centre anchors. Discovery only; any improvement
needs the independent scalar/phase/global/invoice checkers before admission.
Prepared for Rohan Arun with OpenAI Codex assistance; gk primitives retain source notices.
"""
from pathlib import Path
import sys,json,gzip,copy,math,hashlib
R=Path(__file__).resolve().parent;O=R/'trace550-minimum-frames';O.mkdir(exist_ok=False);P=R/'source550-review/local/vendor/gk';sys.path.insert(0,str(P));import gk_word as g,gk_common as c;g.V=c.V=112;g.DATA=c.DATA=7168
source=R/'pr550-independent314/local/candidate/FULL-WORD.json.gz';w=json.loads(gzip.decompress(source.read_bytes()));old=copy.deepcopy(w);before=g.profile(w);V=len(w['ports']);n=2*V+w['report']['R'];cur=[g.basis([p])for p in w['ports']]+[()]*(n-V)
for r,F in w.get('start_extra',{}).items():cur[int(r)]=g.basis(F)
anchors={}
for r,F in zip(w['centers'],w['center_frames']):
 ix=max(i for i,e in enumerate(w['A'])if r in(e[1:3]if e[0]=='add'else e[1:2]));anchors[ix]=g.basis(w['A'][ix][-1])
changes=[]
for sec in ['A','B']:
 if sec=='B':
  for r,F in zip(w['centers'],w['center_frames']):assert cur[r]==g.basis(F)
  for r in range(V,2*V):assert cur[r]==g.basis(w.get('target_levels',{}).get(str(r-V),[]))
 for i,e in enumerate(w[sec]):
  rs=e[1:3]if e[0]=='add'else e[1:2];F=g.basis([x for r in rs for x in cur[r]])
  if sec=='A'and i in anchors:F=anchors[i]
  assert g.span(F)<=g.span(g.basis(e[-1]))
  for r in rs:assert g.span(cur[r])<=g.span(F)
  if F!=g.basis(e[-1]):changes.append(dict(section=sec,index=i,old=e[-1],new=list(F)));e[-1]=list(F)
  for r in rs:cur[r]=F
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not V<=e[1]<2*V];after=g.profile(w);assert sum(r*n for r,n in before.items())==sum(r*n for r,n in after.items());w['report']['local_profile']=dict(after)
(O/'WORD.json.gz').write_bytes(g.dump(w));b=float('0.001593581126479114854212');cost=lambda h:sum(n*r*((73/r)**b-1)for r,n in h.items());ans=dict(status='COMPLETE_CAUSAL_MINIMUM_FRAME_SCREEN_NOT_ADMISSION',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),before=dict(before),after=dict(after),changes=changes,fee_delta=cost(after)-cost(before),scope='Same scalar instructions, helper starts, target levels and anchored last A touches of centre registers. Rational/global phase and full physical admission remain required for any improving candidate.');(O/'RESULT.json').write_text(json.dumps(ans,indent=2)+'\n');print({k:v for k,v in ans.items()if k!='changes'},'changed',len(changes))
