"""Replay the package through the terminal-sink stage and dump the post-sink word for discovery/descent2_search.py.
Not run by verify.py. Usage: python3 -B discovery/descent2_dump.py OUT.pkl"""
import sys,importlib.util,pickle
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
run=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(run)
for st in ('descent_transform','target_transform','kernel_transform','restore_transform','sink_transform'):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
W,C=run['W'],run['C']
d=dict(records=run['records'].tobytes(),initial=dict(run['initial_state']),final=dict(run['final_state']),ends=dict(run['helper_endpoints']),A=dict(C.A),B=dict(C.B),dimf=dict(C.dimf),chi=C.chi,cov=C.cov,h=C.h,v=W.v,ZERO=run['ZERO'],FULL=run['FULL'],cats=list(run['physical']['category_names']),physical={k:run['physical'][k] for k in ('paid_histogram','weighted_scalar_events','scalar_projection_sha256')},nregs=len(run['initial_state']))
pickle.dump(d,open(sys.argv[1],'wb'));print('dumped',sys.argv[1])
