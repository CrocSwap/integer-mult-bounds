"""Fresh exact p10 early-restoration screen; PR280/283 mechanism, generic-h port prepared with OpenAI Codex assistance. Apache-2.0."""
if not __debug__:raise SystemExit("assertions required")
import sys,json,hashlib,importlib.util
from pathlib import Path
from array import array
from collections import Counter
sys.dont_write_bytecode=True

def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
HERE=Path(__file__).resolve().parent
m=load('general_math',HERE/'restore_math.py');rt=load('early_screen',HERE/'restore_transform.py')
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--selection',type=Path);args=ap.parse_args();P=args.input;O=args.output;O.mkdir(parents=True,exist_ok=True);S=json.loads((P/'249-states.json').read_text());F=json.loads((P/'frames.json').read_text());h=F['h'];n=S['n'];v=S['v'];frames={int(k):z for k,z in F['frames'].items()};original_frame_ids=set(frames)
class C:
 def __init__(self):self.frames=frames;self.B={f:z['B']for f,z in frames.items()};self.A={f:z['A']for f,z in frames.items()};self.dimf={f:z['dim']for f,z in frames.items()};self.sub_cache={};self.nd_cache={}
 def sub(self,f,g):
  if f==g:return True
  return self.dimf[f]<=self.dimf[g]and all(m.dot(a,b)==0 for a in self.A[g]for b in self.B[f])
 def nondeg(self,f):
  if f not in self.nd_cache:
   B=self.B[f];ss=[sum(b)for b in B];M=[[9*m.dot(x,y)-ss[i]*ss[j]for j,y in enumerate(B)]for i,x in enumerate(B)];self.nd_cache[f]=len(m.reduce_rows(M,len(B))[0])==len(B)
  return self.nd_cache[f]
class W:
 def __init__(self,C):self.C=C;self.v=v;self.h=h;self.by_basis={tuple(map(tuple,B)):f for f,B in C.B.items()}
 def register(self,rows):
  B,_=m.reduce_rows(rows,h);B=tuple(sorted(map(tuple,B),key=lambda r:next(i for i,x in enumerate(r)if x)))
  if B in self.by_basis:return self.by_basis[B]
  f=max(self.C.frames)+1;A,_=m.kernel(B,h);self.C.frames[f]={'B':list(B),'A':A,'dim':len(B)};self.C.B[f]=list(B);self.C.A[f]=A;self.C.dimf[f]=len(B);self.by_basis[B]=f;return f
c=C();w=W(c);R=array('i');R.frombytes((P/'COHORT249-RECORDS.bin').read_bytes());I={int(k):z for k,z in json.loads((P/'COHORT249-INITIAL.json').read_text()).items()};cats=S['physical']['category_names'];cut,rows,state=rt.screen(R,I,n,v,c,w,cats,S['ZERO'],S['FULL']);entries=[];census=Counter()
for a,b,i,coeff,fa,fb in rows:
 E=w.register(c.B[fa]+c.B[fb]);d=c.dimf[E];ok=d<h and c.nondeg(E);census[(c.dimf[I[a]],c.dimf[fa],c.dimf[fb],d,ok)]+=1
 if ok:entries.append(dict(helper=a,donor=b,record=i,coefficient=coeff,frame=E,rank=d,basis=c.B[E],dims=[c.dimf[I[a]],c.dimf[fa],c.dimf[fb],d],entrance=I[a],helper_frame=fa,donor_frame=fb,incidence=[a,b,coeff]))
entries.sort(key=lambda e:e['helper']);result=dict(status='EXACT_ELIGIBLE_SCREEN_ONLY',h=h,n=n,v=v,input_sha256=hashlib.sha256(R.tobytes()).hexdigest(),record_count=len(R)//6,cut=cut,screened=len(rows),eligible=len(entries),dimensions={str(k):z for k,z in census.items()},endpoint_saving=sum(h-e['rank']for e in entries),eligible_helpers=[e['helper']for e in entries],entries=entries)
(O/'SCREEN.json').write_text(json.dumps(result,indent=2)+'\n');print({k:z for k,z in result.items()if k not in ('entries','eligible_helpers')})
