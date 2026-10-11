"""Run PR484's necessity controls with a retiming-compatible M8 nomination.

The pinned source is unchanged. Retiming may remove its assumed rank-(b+1)
intermediate frame. Choose the smallest available frame containing b, outside
a, of rank at most a; charge both actual codimensions. This keeps the total
rank charge unchanged while violating the same nested-centre-chain clause.
All other source controls and physical/checker code execute literally.
OpenAI Codex; original PR484 Apache-2.0 and author disclosures retained.
Usage: retimed_lemma_mutants.py COMPLEX_SOURCE RETIMED_BASE
"""
from pathlib import Path
import hashlib,json,os,sys
if not __debug__:raise RuntimeError('assertions must remain enabled')
S,B=map(lambda p:Path(p).resolve(),sys.argv[1:])
C=S/'code/lemmaG';p=C/'lg_mutants.py';source=p.read_text()
old="X = next(f for f in range(len(Fr.F)) if Fr.dim[f] == Fr.dim[b] + 1 and Fr.sub(b, f) and not Fr.sub(f, a))"
new="X = min((f for f in range(len(Fr.F)) if Fr.dim[b] < Fr.dim[f] <= Fr.dim[a] and Fr.sub(b, f) and not Fr.sub(f, a)), key=lambda f:(Fr.dim[f],f))"
old_step="['center', kdeep, X, b, 1]"
new_step="['center', kdeep, X, b, Fr.dim[X] - Fr.dim[b]]"
assert source.count(old)==source.count(old_step)==1
adapted=source.replace(old,new).replace(old_step,new_step)
os.environ['LG_BASE']=str(B);sys.path.insert(0,str(C))
exec(compile(adapted,str(p)+' [M8 nomination adapter]','exec'),{'__name__':'__main__','__file__':str(p)})
result=json.loads(Path('MUTANTS.json').read_text())
assert len(result)==14 and all(m['rejected']for m in result)
m8=next(m for m in result if m['mutant'].startswith('M8 '))
assert 'G3'in m8['checker_flags']
report=dict(status='PASS_ALL_14_RETIMED_LEMMA_G_NECESSITY_CONTROLS',pinned_source_sha256=hashlib.sha256(source.encode()).hexdigest(),executed_source_sha256=hashlib.sha256(adapted.encode()).hexdigest(),source_substitutions=[dict(old=old,new=new),dict(old=old_step,new=new_step)],mutants_sha256=hashlib.sha256(Path('MUTANTS.json').read_bytes()).hexdigest(),controls=result)
Path('MUTANT-ADAPTER-RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],flush=True)
