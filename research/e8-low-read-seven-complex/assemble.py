#!/usr/bin/env python3
"""Recompute the exact 47-constraint outer assembly from frozen receipts."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json,hashlib
D=Path(__file__).resolve().parent
r=json.loads((D/'proof/price/kappa.json').read_text()); fjson=json.loads((D/'proof/price/finite.json').read_text()); b3=json.loads((D/'complex/b3.json').read_text())
spec=importlib.util.spec_from_file_location('outer',D/'code/outer.py'); outer=importlib.util.module_from_spec(spec); spec.loader.exec_module(outer)
a=F(r['kappa']); bit=F(fjson['bootstrap_chain'][-1]); b=F(b3['b']); eta=F(1,10**12); beta=F(1,10**9)
bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),rows=dict(degree_gap=F(10**6)-F(51*20161,25)))
asm=outer.assembly(bit,b,bridge,a, eta=eta,beta=beta)
assert len(asm['strict_constraints'])==47 and min(asm['strict_constraints'].values())>0
try: outer.assembly(bit,b,bridge,a+F(1,10**18),eta=eta,beta=beta)
except AssertionError: pass
else: raise AssertionError('adjacent grid point admitted')
result=dict(status='PASS_EXACT_47_CONSTRAINT_ASSEMBLY',kappa=str(a),bit_coarse=r['bit_coarse'],complex_coarse=str(b),binding=r['binding'],grid='1/10^18',strict_constraints={k:str(v) for k,v in asm['strict_constraints'].items()},minimum_strict_constraint=str(min(asm['strict_constraints'].values())),adjacent_grid_point_rejected=True,bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':'1'},'rows':{'degree_gap':str(bridge['rows']['degree_gap'])}},source='code/outer.py',AI='OpenAI Codex assistance; inherited PR315/PR363 notices retained')
(D/'proof/assembly.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n'); print(json.dumps({k:result[k] for k in ('status','kappa','minimum_strict_constraint','adjacent_grid_point_rejected')}))
