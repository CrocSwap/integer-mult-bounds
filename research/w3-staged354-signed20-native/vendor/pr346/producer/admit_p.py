"""Admission chain for a complex word built by make_layer_p.py: PR #200's complete complex checker (PR #233 step 3)
and PR #194's contract (PR #233 step 4), using PR #304's verify.py functions unchanged."""
import sys, json, importlib.util, shutil
from pathlib import Path
P304=Path('/home/claude/pr304/research/complex-module-anneal')
root=Path('/home/claude/cx/tree').resolve()
sys.path.insert(0,str(root/'scripts')); sys.path.insert(0,str(P304)); sys.path.insert(0,str(P304/'gx'))
spec=importlib.util.spec_from_file_location('v304',P304/'verify.py'); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
tag=sys.argv[1]; base=Path('/home/claude/cx')/tag; tree=base/'tree-mw'
work=base/'admission'; 
if work.exists(): shutil.rmtree(work)
work.mkdir()
res={}
res['admission']=V.admit(root,tree,work/'cand')
print('ADMISSION',res['admission']['status'][:120],flush=True)
# contract (PR #194 / #233 step 4)
PKG=root/'research/source-assisted-v4'
(PKG/'data').mkdir(exist_ok=True)
(PKG/'data/physical-pairs.json').write_bytes((tree/'references/paired-cube/physical/pairs.json').read_bytes())
shutil.copyfile(base/'kernel-pairs-mw.json',PKG/'data/kernel-pairs.json')
flow=tree/'flow.json'; witness=tree/'flow.witness.json'; lift=base/'lift.json'
cprof=work/'complex-profile.json'
V.run(root,PKG/'contract_v4.py','--tree',tree,'--cache',tree/'cache','--witness',witness,'--flow-profile',flow,'--lift-profile',lift,'--out',cprof)
cd=json.loads(cprof.read_text()); fd=json.loads(flow.read_text())
bad=[k for k,c in cd['contract_checks'].items() if c in (False,'FAIL')]
print('CONTRACT checks',len(cd['contract_checks']),'failed',bad,'| physical_R',cd['physical_R'],'== flow',fd['new_R'],'| histogram equal',cd['child_histogram']==fd['child_histogram'],flush=True)
json.dump(dict(admission=res['admission'],contract_checks=cd['contract_checks'],physical_R=cd['physical_R']),open(work/'admission-summary.json','w'),indent=1,default=str)
