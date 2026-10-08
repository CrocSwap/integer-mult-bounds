#!/usr/bin/env python3
"""Exact capped-mass check for all concave powers, conditional on input profiles.

Uses the elementary discrete concavity identity written in PROOF.md. Prepared
with substantial OpenAI Codex assistance. Capped-mass comparison format follows
rfu08's concurrent PR64 audit, independently reconstructed here. Apache-2.0.
"""
from pathlib import Path
import json
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent
old=json.loads((HERE/'comparison-pr63.json').read_text())
new=json.loads((HERE/'selected-arithmetic.json').read_text())['profile']
assert (old['m'],old['W'])==(new['m'],new['W'])
a={int(t):n for t,n in old['child_multiplicities'].items()}
b={int(t):n for t,n in new['child_multiplicities'].items()}
delta={t:b.get(t,0)-a.get(t,0) for t in sorted(set(a)|set(b)) if b.get(t,0)!=a.get(t,0)}
assert sum(t*n for t,n in delta.items())==0
caps={k:sum(min(k,t)*n for t,n in delta.items()) for k in range(1,max(set(a)|set(b))+1)}
assert all(x<=0 for x in caps.values()) and any(x<0 for x in caps.values())
record=json.loads((HERE/'concavity-screen.json').read_text())
assert delta=={int(k):v for k,v in record['delta_new_minus_pr63'].items()}
assert caps=={int(k):v for k,v in record['capped_mass_differences'].items()}
print('PASS: selected moment is strictly below PR63 for every saving 0 < a < 1')
