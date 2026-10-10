# Exact rational moment certification (PR234 cost engine) for a word's five-stage profile.
import sys, json, collections
sys.path.insert(0,'/home/claude/pr234/research/five-stage-source-bound-v8/code')
sys.path.insert(0,'/home/claude/work/eval')
import importlib.util
spec=importlib.util.spec_from_file_location('fsc','/home/claude/pr234/research/five-stage-source-bound-v8/code/five_stage_bit_cost_20261009.py')
M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from cost import load_snapshot, local_profile, five_stage
from fractions import Fraction as F
d=sys.argv[1]
s,fr,dim,rec=load_snapshot(d)
H,resid,v=local_profile(rec,s,dim)
prof,W,m,deficit=five_stage(H,resid,v)
Wf=F(4*v)+F(resid,24)
prof={int(k):int(n) for k,n in prof.items()}
scale=Wf.denominator
profS={k:n*scale for k,n in prof.items()}
r=M.certify(profS,120,int(Wf*scale),bad=True)
print(json.dumps({'W':str(Wf),'deficit':float(deficit),'saving_lower':r['lower'],'saving_upper':r['upper']},indent=1))
