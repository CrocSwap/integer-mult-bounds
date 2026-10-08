#!/usr/bin/env python3
"""Bind the unchanged Lean rational companion to this freshly composed finite certificate."""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
import json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'research/aligned-composition';L=D/'lean'
read=lambda p:json.loads(p.read_text())
def typed(x):
 if isinstance(x,dict):return {str(k):typed(v) for k,v in x.items()}
 if isinstance(x,list):return [typed(v) for v in x]
 if isinstance(x,(str,int)):
  try:return Fraction(x)
  except (ValueError,ZeroDivisionError):pass
 return x
selection=read(D/'discovery-selection.json');data=read(L/'input.json');cert=read(ROOT/'certificates/aligned-composition-kappa.json');best=data['best']
assert data['frozen_selection_sha256']==sha256((D/'discovery-selection.json').read_bytes()).hexdigest()
assert data['portfolio_sha256']==selection['portfolio_sha256'] and data['axes']==selection['axes']
for key in ('kappa','bit_saving','finite_bridge'):assert typed(best[key])==typed(cert[key]),key
for key in ('m','N','W','L','total_rank','deficit','maxchild','child_multiplicities'):assert typed(best['bit'][key])==typed(cert['bit'][key]),key
for key in ('assembly','eventual_bounds','kappa','next_kappa','next_kappa_rejection'):assert typed(best['assembly'][key])==typed(cert[key]),key
for original,current in (('accepted_moment','moment'),('rejected_moment','excluded_moment')):assert typed(best[original])==typed(cert['bit'][current]),original
for h in (23,25):assert data['axes'][str(h)]['paid_profile']==read(ROOT/f'certificates/aligned-composition-profiles-{h}.json')
module=ROOT/'formal/lean/KappaCheck/AlignedFrameComposition.lean';source=module.read_bytes();digest=sha256(source).hexdigest();assert digest=='282b1500f96c4ac8ac5dad5da844296ad41be109edcaca0310730304b50ca357'
with tempfile.TemporaryDirectory(prefix='aligned-lean-') as temp:
 out=Path(temp)
 for n in ('generate.py','input.json'):(out/n).write_bytes((L/n).read_bytes())
 subprocess.run([sys.executable,str(out/'generate.py')],cwd=out,check=True,capture_output=True,text=True)
 assert (out/'AlignedFrameComposition.lean').read_bytes()==source
 assert (out/'input.json').read_bytes()==(L/'input.json').read_bytes()
proofs=re.findall(rb'^theorem (\S+)',source,re.M);assert len(proofs)==197
expected={f'KappaCheck.AlignedFrameComposition.{p.decode()}' for p in proofs}
audit=(ROOT/'formal/lean/AuditAll.lean').read_text();actual=set(re.findall(r'^#print axioms (KappaCheck\.AlignedFrameComposition\.\S+)',audit,re.M));assert actual==expected
for n in ('verification.json','independent-audit.json'):assert read(L/n)['source_sha256']==digest
receipt=dict(status='PASS exact Lean source regeneration and all finite input/certificate links',source_sha256=digest,input_sha256=sha256((L/'input.json').read_bytes()).hexdigest(),theorems=197,axiom_audit_entries=197,scope='Rational arithmetic linkage only; Lean compilation and axiom execution are the separate formal-historical-verify gate. Physical arrays, real log/exp validity and all-size transfer remain external.')
(ROOT/'certificates/aligned-composition-lean-validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
