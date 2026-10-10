#!/usr/bin/env python3
"""Physical-layer search under the FLOW objective: run our descent (physical_opt via harness.descend) on an aligned
cache (graph/frames/selection/record of the source-aligned word), write the resulting physical frames and reuse pairs
into a copy of the aligned tree, and price with PR184's complex_frame_flow.py. Discovery only (float)."""
from pathlib import Path
import sys,os,json,time,argparse,shutil,subprocess,tempfile
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import harness
ap=argparse.ArgumentParser();ap.add_argument('--aligned',type=Path,required=True,help='aligned tree (with cache/ and references/paired-cube/physical/)')
ap.add_argument('--sa',default=os.environ.get('SA_TREE',str(Path.home()/'sa-flow')));ap.add_argument('--py',default=os.environ.get('SA_PY',sys.executable))
ap.add_argument('--light',action='store_true');ap.add_argument('--deep',type=int,default=0);ap.add_argument('--mw',type=int,default=0);ap.add_argument('--pair-first',action='store_true')
ap.add_argument('--seed-frames',action='store_true',help='start from the tree\'s own physical frames');ap.add_argument('--tag',default='');ap.add_argument('--out',default='flow-frames.jsonl');ap.add_argument('--keep',type=Path,default=None)
a=ap.parse_args();SA=Path(a.sa)
t=time.monotonic();cache=a.aligned/'cache'
g,w,word,row=(json.loads((cache/n).read_text()) for n in ('graph.json','frames.json','selection.json','record.json'))
seed=None
if a.seed_frames:seed=json.loads((a.aligned/'references/paired-cube/physical/frames.json').read_text())['frames']
prof,frames,pairs,stats=harness.descend(g,w,row,word,a.light,a.deep,seed,a.mw,a.pair_first)
pre=harness.root(prof);t1=time.monotonic()-t
work=Path(tempfile.mkdtemp(prefix='flowframes-'))
try:
 tree=work/'tree';shutil.copytree(a.aligned,tree)
 (tree/'references/paired-cube/physical/frames.json').write_text(json.dumps(dict(frames=[[i,list(F)] for i,F in frames]),separators=(',',':'))+'\n')
 (tree/'references/paired-cube/physical/pairs.json').write_text(json.dumps(dict(pairs=[list(p) for p in pairs]),separators=(',',':'))+'\n')
 r=subprocess.run([a.py,'-B',str(SA/'research/source-assisted/decision/complex_frame_flow.py'),'--tree',str(tree),'--cache',str(tree/'cache'),'--out',str(work/'flow.json'),'--witness','--purify-source-donors','--recycle-kernels'],capture_output=True,text=True)
 if r.returncode:res=dict(tag=a.tag,error='flow: '+r.stderr[-500:],pre_root=pre)
 else:
  f=json.loads((work/'flow.json').read_text());res=dict(tag=a.tag,pre_root=pre,flow_root=f['numerical_local_root'],new_R=f['new_R'],new_W=f['new_W'],W_pre=prof['W_per_vertex'],pairs=len(pairs),changed=len(frames),stats=stats,seconds=time.monotonic()-t,descent_seconds=t1,opts=dict(light=a.light,deep=a.deep,mw=a.mw,pair_first=a.pair_first,seed_frames=a.seed_frames,PHI_ALPHA=os.environ.get('PHI_ALPHA'),DESCENT_SEED=os.environ.get('DESCENT_SEED')))
  if a.keep:
   a.keep.mkdir(parents=True,exist_ok=True)
   for n in ('frames.json','pairs.json'):shutil.copy2(tree/'references/paired-cube/physical'/n,a.keep/n)
   shutil.copy2(work/'flow.json',a.keep/'flow.json')
finally:shutil.rmtree(work,ignore_errors=True)
open(H/a.out,'a').write(json.dumps(res)+'\n');print(json.dumps({k:res.get(k) for k in ('tag','pre_root','flow_root','new_W','W_pre','pairs','changed','seconds','error')}),flush=True)
