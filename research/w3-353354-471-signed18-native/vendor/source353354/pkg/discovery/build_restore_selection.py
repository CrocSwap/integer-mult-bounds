"""Freeze restore-selection.json: run the pipeline through the kernel stage, apply the fresh PR280 screen on the actual
word and record the 440 helper/donor/join rows and the local histogram delta. Not run by verify.py.
Usage: python3 -B discovery/build_restore_selection.py"""
import sys,json,importlib.util,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
producer=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(producer)
for st in ('descent_transform','target_transform'):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
rt=load('portable527_restore',ROOT/'restore_transform.py')
W,C=run['W'],run['C'];old=run['records'];v=W.v;n=2*v+len(run['context']['regs']);initial=dict(run['initial_state'])
cats=list(run['physical']['category_names'])
cut,rows,state=rt.screen(old,initial,n,v,C,W,cats,run['ZERO'],run['FULL'])
entries=[]
for a,b,i,c,fa,fb in rows:
    E=W.register([list(x)for x in C.B[fa]]+[list(x)for x in C.B[fb]])
    if C.dimf[E]==W.h or not C.nondeg(E):continue
    entries.append(dict(helper=a,donor=b,coefficient=c,incidence=[old[6*i+j]for j in(1,2,3)],rank=C.dimf[E],basis=[list(x)for x in C.B[E]],dims=[C.dimf[initial[a]],C.dimf[fa],C.dimf[fb],C.dimf[E]]))
sel=dict(status='GEN5_EARLY_RESTORATION_PR280_SCREEN',n=n,v=v,input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),input_scalar_sha256=run['physical']['scalar_projection_sha256'],cut=cut,selected=len(entries),entries=entries,expected_local_delta={})
out,initial2,final,order,cats2,proof,_,_=rt.transform(run,sel)
hist=Counter();
for k in range(0,len(out),6):
    if out[k]==0 and out[k+4]:hist[out[k+4]]+=1
    elif out[k]==2:hist[out[k+5]]+=1
d=Counter(hist);d.subtract({int(r):c for r,c in run['physical']['paid_histogram'].items()})
sel['expected_local_delta']={str(r):c for r,c in sorted(d.items())if c}
(ROOT/'restore-selection.json').write_text(json.dumps(sel)+'\n')
print('selected',len(entries),'cut',cut,'delta',sel['expected_local_delta'],'dims',Counter(tuple(e['dims'])for e in entries))
