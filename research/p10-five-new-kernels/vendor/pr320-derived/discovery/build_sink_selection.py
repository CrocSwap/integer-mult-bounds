"""Freeze sink-selection.json: run the pipeline through the restoration stage, apply the fresh terminal-sink screen
(PR283 rule plus: no target of the set is ever a scalar/COPY source; pivot unwritten on the interval) and record the
sinks and the local histogram delta. Not run by verify.py. Usage: python3 -B discovery/build_sink_selection.py"""
import sys,json,importlib.util,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
producer=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(producer)
for st in ('descent_transform','target_transform','kernel_transform','restore_transform'):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
sm=load('portable527_sink',ROOT/'sink_transform.py')
W=run['W'];old=run['records'];v=W.v;regs=run['context']['regs'];n=2*v+len(regs)
entry,rows=sm.screen(old,dict(run['initial_state']),dict(run['final_state']),n,v,list(run['physical']['category_names']),run['ZERO'],run['FULL'])
used=set();keep=[]
for r in rows:
    if used&set(r['targets']):continue
    used.update(r['targets']);keep.append(r)
assert len(keep)==len(rows)
sel=dict(status='GEN5_TERMINAL_SINKS_PR283_SCREEN',n=n,v=v,input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),input_scalar_sha256=run['physical']['scalar_projection_sha256'],entry=entry,selected=len(keep),
    sinks=[dict(role=regs[r['stream']-2*v],stream=r['stream'],targets=r['targets'],pivot=r['pivot'],root_frame_basis=[list(x)for x in run['C'].B[r['root_frame']]],forward_writes=len(r['writes']),cleanups=len(r['cleanups']))for r in keep],expected_local_delta={})
out,initial,final,ends,rows2,ctx2,cats,proof,nn,_,mp=sm.transform(run,sel)
hist=Counter()
for k in range(0,len(out),6):
    if out[k]==0 and out[k+4]:hist[out[k+4]]+=1
    elif out[k]==2:hist[out[k+5]]+=1
d=Counter(hist);d.subtract({int(r):c for r,c in run['physical']['paid_histogram'].items()})
sel['expected_local_delta']={str(r):c for r,c in sorted(d.items())if c}
(ROOT/'sink-selection.json').write_text(json.dumps(sel,indent=1)+'\n')
print('selected',len(keep),'entry',entry,'delta',sel['expected_local_delta'],'removed roles',proof['removed_roles'],'new n',nn)
