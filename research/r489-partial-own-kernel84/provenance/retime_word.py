"""OpenAI Codex: fixed-scalar-word common-frame retiming discovery.
Keep selected helper entrances, scalar gates and fixed boundary labels unchanged.
No claim of admission until exact canonical/program/phase/controller replay.
"""
import json,gzip,sys,copy,hashlib
from pathlib import Path
from collections import Counter
BASE=Path('/private/tmp/pr484-independent-full-proof/gauge80-kernel42')
CODE=Path('/private/tmp/pr484-independent-source/research/e8-complex-gauge-kernel/code');sys.path.insert(0,str(CODE));import gk_word as G
P=Path(__file__).resolve().parent/'retiming';P.mkdir(exist_ok=True)
w=json.load(gzip.open(BASE/'split-centres/FULL-WORD.json.gz'));n=240+w['report']['R'];V=120
basis=G.basis;span=G.span;FULL=basis(range(1,512));final=[FULL]*120+[G.perp(p)for p in w['ports']]+[FULL]*w['report']['R'];start=[basis([p])for p in w['ports']]+[()]*120+[basis(w.get('start_extra',{}).get(str(i),[]))for i in range(240,n)]

def registers(e):return [e[1],e[2]]if e[0]=='add'else[e[1]]
def backward(seq,upper):
 cur=upper.copy();out=copy.deepcopy(seq)
 for e in reversed(out):
  rs=registers(e);F=basis(set.intersection(*(span(cur[r])for r in rs)));assert span(basis(e[-1]))<=span(F)
  e[-1]=list(F)
  for r in rs:cur[r]=F
 return out,cur

def forward(seq,lower):
 cur=lower.copy();out=copy.deepcopy(seq)
 for e in out:
  rs=registers(e);F=basis([v for r in rs for v in cur[r]]);assert span(F)<=span(basis(e[-1])),(rs,F,e[-1])
  e[-1]=list(F)
  for r in rs:cur[r]=F
 return out,cur

def upper_word(word):
 z=copy.deepcopy(word);z['B'],cutupper=backward(z['B'],final)
 for r,F in zip(z['centers'],z['center_frames']):cutupper[r]=basis(F)
 for t in range(V):cutupper[V+t]=basis(z.get('target_levels',{}).get(str(t),[]))
 z['A'],before=backward(z['A'],cutupper)
 assert all(span(a)<=span(b)for a,b in zip(start,before))
 return z

def lower_word(word):
 z=copy.deepcopy(word);z['A'],cur=forward(z['A'],start)
 for r,F in zip(z['centers'],z['center_frames']):
  F=basis(F)
  if cur[r]!=F:z['A'].append(['scale',r,1,1,list(F)]);cur[r]=F
 for t in range(V):
  r=V+t;F=basis(z.get('target_levels',{}).get(str(t),[]))
  if cur[r]!=F:z['A'].append(['scale',r,1,1,list(F)]);cur[r]=F
 z['B'],cur=forward(z['B'],cur)
 return z

def finish(name,z):
 p=G.profile(z);z['report']['local_profile']={str(r):k for r,k in sorted(p.items())};z['cleanup']=[G.inverse(e,FULL)for e in reversed(z['A']+z['B'])if not V<=e[1]<2*V]
 ws=G.widths_of(z);live,gp=G.global_profile(p,ws);z['report']['global_profile']={str(r):k for r,k in sorted(gp.items())};z['report']['live']=live
 fn=P/(name+'.json.gz');fn.write_bytes(G.dump(z));oldp={int(r):k for r,k in w['report']['local_profile'].items()};delta={r:p[r]-oldp.get(r,0)for r in set(p)|set(oldp)};delta={r:k for r,k in delta.items()if k}
 print(name,dict(sorted(p.items())),'delta',delta,'mass',sum(r*k for r,k in p.items()),'gates',len(z['A'])+len(z['B']),flush=True)
 return dict(name=name,sha256=hashlib.sha256(fn.read_bytes()).hexdigest(),profile=dict(sorted(p.items())),delta=delta,rank_mass=sum(r*k for r,k in p.items()),scalar_gate_count=len(z['A'])+len(z['B']))
out=[finish('original',w),finish('upper',upper_word(w)),finish('lower',lower_word(w)),finish('upper-lower',lower_word(upper_word(w))),finish('lower-upper',upper_word(lower_word(w)))]
(P/'SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
