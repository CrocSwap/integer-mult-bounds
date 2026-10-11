"""Export the p10bs word after parity and after each transcript stage as PR249 snapshots (records.bin, states.json, frames.json) + meta.pkl.
usage: export_stages.py PKG OUTDIR"""
import sys,json,pickle,hashlib,importlib.util,time
from pathlib import Path
import numpy as np
P=Path(sys.argv[1]).resolve();O=Path(sys.argv[2]).resolve();sys.path.insert(0,str(P));sys.dont_write_bytecode=True
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
t=time.monotonic()
ctx=load('portable527_prepare',P/'prepare.py').prepare()
context=dict(ctx)
run=load('portable527_physical',P/'code/physical527.py').run(context,context['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',P/'parity_transform.py').run(run)
ST=load('portable527_bitstages',P/'portable_bit.py').STAGES
rm=load('portable527_reorder',P/'reorder_transform.py')
def dump(tag,run):
    D=O/tag;D.mkdir(parents=True,exist_ok=True)
    W,C=run['W'],run['C']
    arr=np.asarray(run['records'],dtype='<i4');(D/'249-records.bin').write_bytes(arr.tobytes())
    init={int(k):int(v) for k,v in run['initial_state'].items()}
    final=dict(init);used=set(init.values())
    for k in range(0,len(arr),6):
        op,a,b,c,f,z=[int(x) for x in arr[k:k+6]]
        if op==0: final[a]=c;used.update((b,c))
        elif op==1: used.add(f)
        elif op in(2,3): used.update((c,f))
    used.add(run['ZERO']);used.add(run['FULL'])
    st=dict(initial={str(k):v for k,v in init.items()},final={str(k):v for k,v in final.items()},ZERO=run['ZERO'],FULL=run['FULL'],n=len(init),v=W.v,
            record_count=len(arr)//6,record_sha256=hashlib.sha256(arr.tobytes()).hexdigest())
    st['source_covectors']=[[int(x) if float(x).is_integer() else str(x) for x in C.cov[t]] for t in range(W.v)]
    json.dump(st,open(D/'249-states.json','w'))
    json.dump(dict(h=W.h,frames={str(f):dict(B=[list(map(int,b)) for b in C.B[f]],A=[list(map(int,a)) for a in C.A[f]],dim=C.dimf[f]) for f in sorted(used)}),open(D/'frames.json','w'))
    meta=dict(ends={int(k):int(v) for k,v in run.get('helper_endpoints',{}).items()},keys=sorted(run.keys()),final_state={int(k):int(v) for k,v in run['final_state'].items()} if 'final_state' in run else None)
    pickle.dump(meta,open(D/'meta.pkl','wb'))
    print('dumped',tag,'records',len(arr)//6,'n',len(init),'frames',len(used),round(time.monotonic()-t),flush=True)
dump('00-parity',run)
for i,st in enumerate(ST):
    run=rm.run(run,tag=st) if st.startswith('reorder') else load('portable527_'+st,P/(st+'_transform.py')).run(run)
    dump('%02d-%s'%(i+1,st),run)
