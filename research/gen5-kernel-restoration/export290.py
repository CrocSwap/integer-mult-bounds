import sys
if not __debug__:raise SystemExit("Assertions must be enabled")
sys.dont_write_bytecode=True
"""Content-checked receipt adapter; does not admit a new mathematical candidate."""
from pathlib import Path
import json,gzip,struct,hashlib,argparse
from collections import Counter
import sympy as S

ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--base-export',type=Path,required=True);args=ap.parse_args()
p=args.baseline;o=args.output;o.mkdir(exist_ok=False);b=args.base_export
st=json.loads((b/'249-states.json').read_text());fs=json.loads((b/'frames.json').read_text())['frames'];nf={}
def put(f,B,A):
 f=str(f);entry={'dim':len(B),'B':B,'A':A}
 if f in fs:
  assert fs[f]['B']==B and fs[f]['A']==A,('base frame differs',f)
 elif f in nf:assert nf[f]==entry,('new frame differs',f)
 else:nf[f]=entry
for name in ('descent-used-bases.json','target-used-bases.json'):
 for f,e in json.loads((p/name).read_text()).items():put(f,e['basis'],e['annihilator'])
for e in json.loads((p/'kernel-entrances.json').read_text()):
 B=e['basis'];A=[]
 for x in S.Matrix(B).nullspace():
  den=S.ilcm(*[q.q for q in x]);A.append([int(q*den) for q in x])
 # An equivalent annihilator basis is sufficient; existing IDs keep their checked basis.
 f=str(e['frame'])
 if f in nf:
  assert nf[f]['B']==B
 elif f in fs:assert fs[f]['B']==B
 else:put(f,B,A)
raw=gzip.decompress((p/'kernel-records.bin.gz').read_bytes());w=list(struct.iter_unpack('<6i',raw))
binding=json.loads((b/'SOURCE-CONTEXT.json').read_text())
assert binding['kernel_word_sha256']==hashlib.sha256(raw).hexdigest()
initial=json.loads((p/'kernel-initial.json').read_text());assert initial==binding['kernel_initial']
final={str(a):int(f) for a,f in initial.items()}
for k,a,bb,c,f,z in w:
 if k==0:final[str(a)]=c
assert final==st['final'],'PR290 changed retained final endpoints'
# Preserve original baseline initial frames for independently measured entrance savings.
physical=json.loads((p/'physical.json').read_text());hist=physical['paid_histogram']
literal=Counter(e[4] for e in w if e[0]==0 and e[4]);literal.update(e[5] for e in w if e[0]==2)
assert dict(literal)=={int(r):int(c) for r,c in hist.items()}
assert sum(r*c for r,c in literal.items())==physical['paid_rank_mass']==410334
assert len(json.loads((p/'kernel-entrances.json').read_text()))==450
basehist=json.loads((b/'COHORT249-REPLAY.json').read_text())['histogram']
delta={r:int(hist.get(r,0))-int(basehist.get(r,0)) for r in set(hist)|set(basehist)};delta={r:x for r,x in delta.items() if x}
receipt={'histogram':hist,'delta':delta,'new_rank_mass':physical['paid_rank_mass'],'new_entrance_rank':sum(e['rank'] for e in json.loads((p/'kernel-entrances.json').read_text())),'new_records':len(w)}
for name,value in [('249-states.json',st),('frames.json',{'h':24,'frames':fs}),('COHORT249-FRAMES.json',nf),('COHORT249-INITIAL.json',initial),('COHORT249-REPLAY.json',receipt),('COHORT249-SELECTION.json',{'source':'PR290 frozen kernel selection'})]:
 (o/name).write_text(json.dumps(value,separators=(',',':')))
(o/'COHORT249-RECORDS.bin').write_bytes(raw)
(o/'ADAPTER.json').write_text(json.dumps({'word_sha256':hashlib.sha256(raw).hexdigest(),'new_frames':len(nf),'old_frame_basis_equality_checked':True,'final_endpoints_equal':True,'scope':'Receipt adapter only; native and independent replay required.'},indent=2)+'\n')
print((o/'ADAPTER.json').read_text())
