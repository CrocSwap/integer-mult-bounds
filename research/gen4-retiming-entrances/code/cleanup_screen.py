#!/usr/bin/env python3
"""Regenerate the fixed440 gen4 cleanup selection."""
from pathlib import Path
from array import array
from collections import Counter,defaultdict
import json,sys,argparse
if not __debug__: raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).parent))
from cleanup_reference import rational_basis,rank_mod_prime,annihilator
ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--export-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();D=args.output_dir;D.mkdir(parents=True,exist_ok=True);P=args.source_dir;X=args.export_dir
r=array('i');r.frombytes((P/'COHORT249-RECORDS.bin').read_bytes());st=json.loads((X/'gen4-states.json').read_text());n=st['n'];v=st['v'];rows=[1<<j for j in range(n)]+[0];fs=json.loads((X/'frames.json').read_text())['frames'];fs.update(json.loads((P/'COHORT249-FRAMES.json').read_text()));state={int(a):f for a,f in json.loads((P/'COHORT249-INITIAL.json').read_text()).items()}
cut=next(i for i in range(len(r)//6) if r[6*i]==1 and r[6*i+5]==3)
for i in range(cut):
 op,a,b,c,f,z=r[6*i:6*i+6]
 if op==0:state[a]=c
 elif op==1:rows[a]^=rows[b]
 elif op==2:rows[b]=rows[a];state[b]=f
 elif op==3:rows[b]=0;state.pop(b,None)
assert (n,v,cut)==(19930,1760,662145)
assert all(rows[v+j]==(1<<(v+j))^(1<<j) for j in range(v))
print('cut',cut,'target wrong',sum(rows[v+j]!=(1<<(v+j))^(1<<j) for j in range(v)),flush=True)
affected=[0]*n
for a,x in enumerate(rows[:n]):
 x^=1<<a
 if v<=a<2*v:x^=1<<(a-v)
 while x:k=(x&-x).bit_length()-1;x&=x-1;affected[k]+=1
cand=[a for a in range(2*v,n) if not affected[a] and fs[str(state[a])]['dim']<24]
suffix=[1<<a for a in range(n)]+[0];inc=defaultdict(list)
for i in range(cut,len(r)//6):
 op,a,b,c,f,z=r[6*i:6*i+6]
 if op==1:suffix[a]^=suffix[b];inc[a].append((i,a,b));inc[b].append((i,a,b))
 elif op==2:suffix[b]=suffix[a]
 elif op==3:suffix[b]=0
census=Counter();cs=[];newframes={}
for a in cand:
 x=suffix[a]^(1<<a);don=[]
 while x:k=(x&-x).bit_length()-1;x&=x-1;don.append(k)
 census[len(don),max([fs[str(state[b])]['dim'] for b in don]+[0])]+=1
 if len(don)!=1:continue
 b=don[0]
 B=rational_basis(fs[str(state[a])]['B']+fs[str(state[b])]['B']);d=len(B)
 if d==24:continue
 sums=[sum(u) for u in B];gram=[[9*sum(p*q for p,q in zip(u,w))-su*sw for w,sw in zip(B,sums)]for u,su in zip(B,sums)]
 if rank_mod_prime(gram)!=d:continue
 dim_a=fs[str(state[a])]['dim'];dim_b=fs[str(state[b])]['dim']
 frame=900000+len(newframes);newframes[str(frame)]={'dim':d,'B':B,'A':annihilator(B)}
 cs.append(dict(role=a,donors=[b],frame=frame,dim=d,dim_a=dim_a,dim_b=dim_b,incidences=inc[a]))
print('isolated',len(cand),'donor census',census,flush=True)
print('proper one donor',len(cs),'census',Counter((x['dim_a'],x['dim_b'],x['dim'],len(x['incidences']))for x in cs),flush=True)
assert len(cs)==440 and all((e['dim_a'],e['dim_b'],e['dim'],len(e['incidences']))==(22,22,23,1) for e in cs)
assert len({e['donors'][0] for e in cs})==440
assert not {e['role'] for e in cs}.intersection(e['donors'][0] for e in cs)
(D/'screen.json').write_text(json.dumps({'cut':cut,'n':n,'v':v,'candidates':cs,'newframes':newframes},indent=2))
