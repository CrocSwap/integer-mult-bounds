"""Numerical outer assembly with the unchanged bit side and new complex profile.
This cannot improve kappa while the fixed bit coarse saving still binds.
"""
import json,importlib.util
from pathlib import Path
from fractions import Fraction as Q
s=importlib.util.spec_from_file_location('nine_outer','work/pr361/code/engines/outer.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
out=Path('work/complex-nine-native');b=Q(json.loads((out/'INDEPENDENT-TEMPLATE-AUDIT.json').read_text())['coarse_complex']);c=Q(805497555783488,10**18);eta=Q(1,10**12);beta=Q(1,10**9);chain=[Q(384599,10**10)]
for _ in range(3):chain.append((1-c)*c+c*chain[-1])
bridge=dict(proof='work/complex-nine-native/PROOF.txt',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
k=Q(804849251275843,10**18);r=M.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(r['strict_constraints'])==47 and min(r['strict_constraints'].values())>0
try:M.assembly(chain[-1],b,bridge,k+Q(1,10**18),eta=eta,beta=beta)
except AssertionError:pass
else:raise AssertionError('unexpected next kappa')
z=dict(status='PASS_NUMERICAL_OUTER_CHECK_WITH_FIXED_BIT_NO_KAPPA_IMPROVEMENT',bit_coarse=str(c),complex_coarse=str(b),kappa=str(k),strict_constraints={k:str(v) for k,v in r['strict_constraints'].items()},next_grid_rejected=True,scope='Numerical assembly only. The complex proof retains analytic interfaces; no new bit supplier or final combined theorem claimed.')
(out/'OUTER-FIXED-BIT.json').write_text(json.dumps(z,indent=2));print(z['status'])
