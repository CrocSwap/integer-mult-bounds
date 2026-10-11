"""Sink screen (sink_transform.screen) on the word after a given stage prefix (used to find the helpers the kernel
search excludes). Not run by verify.py. usage: python3 -B discovery/sink_screen_at.py . descent_transform,target_transform
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import sys,importlib.util
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve();sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
run=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(run)
for st in sys.argv[2].split(','):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
sm=load('portable527_sink',ROOT/'sink_transform.py')
old=run['records'];W=run['W'];v=W.v;n=2*v+len(run['context']['regs'])
final=dict(run.get('final_state') or run['initial_state'])
if 'final_state' not in run:
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
entry,rows=sm.screen(old,dict(run['initial_state']),final,n,v,list(run['physical']['category_names']),run['ZERO'],run['FULL'])
print('sinks',len(rows),[ (r['stream'],r['targets']) for r in rows])
