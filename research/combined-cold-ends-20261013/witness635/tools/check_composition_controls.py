"""Twelve exact composition repair mutants, with positive control.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json,gzip,copy,importlib.util,contextlib,tempfile,hashlib
from pathlib import Path
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
if not __debug__:raise RuntimeError('Assertions required')
out=args.out;out.mkdir(parents=True,exist_ok=False);root=out.parent
p=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('native',p/'code/hpe_audit_and_transport.py');native=importlib.util.module_from_spec(s);s.loader.exec_module(native)
w=json.loads(gzip.decompress((args.word).read_bytes()))
routing=p/'vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
with tempfile.TemporaryDirectory(dir=root,prefix='positive-') as td:
 with (out/'positive.log').open('w') as log,contextlib.redirect_stdout(log):
  native.run(args.word,routing,Path(td)/'audit')
print('PASS positive',flush=True)
def at(g):
 ix=[i for i,e in enumerate(w['A']) if e==g];assert len(ix)==1,(g,ix);return ix[0]
delayed=at(['add',95,403,1,4,[265,137,96,6]])
repair=json.loads((p/'data/COMPOSITION-REPAIR.json').read_text());assert w['A'][:len(repair)]==repair
cases=[('delayed_release_omitted',delayed,False),('delayed_release_sign_flipped',delayed,True)]+[(f'basis_correction_{i:02d}_omitted',i,False) for i in range(len(repair))]
results=[]
for name,i,flip in cases:
 z=copy.deepcopy(w)
 if flip:z['A'][i][3]*=-1
 else:z['A'].pop(i)
 with tempfile.TemporaryDirectory(dir=root,prefix='control-') as td:
  td=Path(td);raw=td/'raw.json.gz';raw.write_bytes(gzip.compress(json.dumps(z).encode()))
  with (out/(name+'.log')).open('w') as log,contextlib.redirect_stdout(log):
   try:native.run(raw,routing,td/'audit')
   except AssertionError as exc:
    results.append(dict(name=name,status='REJECTED',reason=str(exc),gate_index=i,original_gate=w['A'][i]));print('EXPECTED REJECTION',exc)
   else:raise RuntimeError('mutant accepted '+name)
 print(results[-1],flush=True)
(out/'CONTROLS.json').write_text(json.dumps({'status':'PASS_TWELVE_COMPOSITION_CONTROLS','input_content_sha256':hashlib.sha256(gzip.decompress((args.word).read_bytes())).hexdigest(),'auditor_sha256':hashlib.sha256((p/'code/hpe_audit_and_transport.py').read_bytes()).hexdigest(),'positive_pass':True,'positive_log':'positive.log','rejected':results},indent=2)+'\n')
