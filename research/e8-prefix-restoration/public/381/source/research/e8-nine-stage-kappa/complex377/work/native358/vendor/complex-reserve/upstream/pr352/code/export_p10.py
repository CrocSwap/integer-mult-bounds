"""Export PR315's p=10 local bit word as a PR249-format snapshot (records.bin, states.json, frames.json)."""
import sys, json, time, gzip, hashlib, importlib.util
from pathlib import Path
P=Path(sys.argv[1]).resolve(); D=Path(sys.argv[2]).resolve(); D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(P)); sys.dont_write_bytecode=True
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m
t=time.monotonic()
ctx=load('p527prep',P/'prepare.py').prepare(); print('prepared',round(time.monotonic()-t),flush=True)
phys=load('p527phys',P/'code/physical527.py'); context=dict(ctx)
prod=phys.run(context,context['SOURCE_TEXT'],output_dir=None); print('physical',round(time.monotonic()-t),flush=True)
run=load('p527par',P/'parity_transform.py').run(prod,output_dir=None); print('parity',round(time.monotonic()-t),flush=True)
print('run keys',sorted(run.keys()))
rec=run['records']; print('records',len(rec)//6, type(rec))
import numpy as np
arr=np.asarray(rec,dtype='<i4')
(D/'249-records.bin').write_bytes(arr.tobytes())
init=run.get('initial_state') or prod.get('initial_state')
print('initial_state', None if init is None else len(init))
C=context['C']
used=set(init.values()) if init else set()
final=dict(init) if init else {}
for k in range(0,len(arr),6):
    op,a,b,c,f,z=[int(x) for x in arr[k:k+6]]
    if op==0: final[a]=c; used.update((b,c))
    elif op==1: used.add(f)
    elif op in (2,3): used.update((c,f))
W=context['W']
st=dict(initial=init,final=final,ZERO=run.get('ZERO',prod.get('ZERO')),FULL=run.get('FULL',prod.get('FULL')),
        n=len(init) if init else None,v=W.v,record_count=len(arr)//6,record_sha256=hashlib.sha256(arr.tobytes()).hexdigest())
json.dump(st,open(D/'249-states.json','w'))
json.dump(dict(h=W.h,frames={str(f):dict(B=C.B[f],A=C.A[f],dim=C.dimf[f]) for f in sorted(used)}),open(D/'frames.json','w'))
print('exported frames',len(used),'n',st['n'],'v',st['v'],'ZERO',st['ZERO'],'FULL',st['FULL'],round(time.monotonic()-t))
import pickle; pickle.dump(dict(physical=run.get('physical'),keys=sorted(run.keys())),open(D/'run-meta.pkl','wb'))
st['source_covectors']=[list(map(int,C.cov[t])) if all(float(x).is_integer() for x in C.cov[t]) else [str(x) for x in C.cov[t]] for t in range(W.v)]
json.dump(st,open(D/'249-states.json','w'))
print('cov sample',st['source_covectors'][0])
