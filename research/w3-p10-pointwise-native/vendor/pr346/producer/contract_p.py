import sys, json, importlib.util, shutil
from pathlib import Path
P304=Path('/home/claude/pr304/research/complex-module-anneal')
root=Path('/home/claude/cx/tree').resolve()
spec=importlib.util.spec_from_file_location('v304',P304/'verify.py'); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
base=root/sys.argv[1]; tree=base/'tree-mw'
PKG=root/'research/source-assisted-v4'; (PKG/'data').mkdir(exist_ok=True)
(PKG/'data/physical-pairs.json').write_bytes((tree/'references/paired-cube/physical/pairs.json').read_bytes())
shutil.copyfile(base/'kernel-pairs-mw.json',PKG/'data/kernel-pairs.json')
cprof=base/'complex-profile.json'
V.run(root,PKG/'contract_v4.py','--tree',tree,'--cache',tree/'cache','--witness',tree/'flow.witness.json','--flow-profile',tree/'flow.json','--lift-profile',base/'lift.json','--out',cprof)
cd=json.loads(cprof.read_text()); fd=json.loads((tree/'flow.json').read_text())
bad=[k for k,c in cd['contract_checks'].items() if c in (False,'FAIL')]
print('CONTRACT checks',len(cd['contract_checks']),'failed',bad,'| physical_R',cd['physical_R'],'flow',fd['new_R'],'| histogram equal',cd['child_histogram']==fd['child_histogram'])
