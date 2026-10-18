#!/usr/bin/env python3
"""Independent direct rank-term assembly, using only invoice's rational oracle."""
from fractions import Fraction as F
from pathlib import Path
from math import isqrt
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location('independent_invoice_oracle', PACKAGE/'invoice/verify.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
N, H, L, M = 30960, 17, 5, 81
Q, PAD = divmod(M, H)
CAP = isqrt((M*M-1)//2)
selected = F(json.loads((ROOT/'certificates/selected-result.json').read_text())['kappa'])
targets = {'selected_frontier1094': selected,
           'discussion_pr1424_title': F('0.001676855229071321886206381217337893')}
cases = {
 'h6_paper_screen': ([16], [16], {17:256,15:560}, []),
 'conservative_encoder': ([1,15], [1,15], {17:256,15:560},
    [(28800,[1,8,8]),(1920,[9,8]),(13440,[9,6,2]),(560,[15,2]),(256,[17])]),
 'full_center_fallback': ([16], [1,7,8], {17:816}, [(816,[17])]),
}
expected = {'selected_frontier1094': [88765,41810,66313],
            'discussion_pr1424_title': [88409,41454,65990]}
receipt = json.loads((PACKAGE/'helper/CHARGED-SCREEN.json').read_text())

def check(value, message):
    if not value:
        raise ValueError(message)

def helper(profile):
    check(sum(profile)==H, 'ordinary full residual')
    return [(F(L*a),a) for a in profile] + [(F(L*PAD,Q),PAD)]

rows = []
for index, (name, (source,target,hist,groups)) in enumerate(cases.items()):
    # L5 paired data idle slots are 32, 32, 16, all below strict child cap57.
    base = [(F(N*L*a),a) for a in source+target]
    base += [(F(L*a*count),a) for a,count in hist.items()]
    base += [(F(2*N*a),a) for a in [32,32,16]]
    bill = sum(a*count for a,count in hist.items())
    deficit = (L-1)*N-L*bill
    stock = F((L-1)*N)
    for count, path in groups:
        base += [(count*mass,rank) for mass,rank in helper(path)]
        stock += F(L*count,Q)
    unit = helper([1,7,8,1])
    check(sum(mass for mass,rank in base)==M*stock-deficit, 'complete baseline rank mass')
    check(sum(mass for mass,rank in unit)==F(L*M,Q), 'helper rank mass includes pad')
    check(all(0<rank<=CAP for mass,rank in base+unit), 'all actual children obey strict cap')
    for target_name,k in targets.items():
        alpha=k/(1-k)
        bl,bu=oracle.pressure(base,M,alpha)
        ul,uu=oracle.pressure(unit,M,alpha)
        low,high=(deficit-bu)/uu,(deficit-bl)/ul
        capacity=oracle.ceil_fraction(low)-1
        check(capacity==oracle.ceil_fraction(high)-1, 'unique strict integer capacity')
        check(capacity==expected[target_name][index], 'announced capacity independently matches')
        pass_slack=(deficit-bu-capacity*uu,deficit-bl-capacity*ul)
        fail_slack=(deficit-bu-(capacity+1)*uu,deficit-bl-(capacity+1)*ul)
        check(pass_slack[0]>0>fail_slack[1], 'adjacent strict signs')
        recorded=next(r for r in receipt['records'] if r['baseline']==name and r['stages']==L and r['target_name']==target_name)
        check(recorded['stock']==str(stock) and recorded['deficit']==deficit and recorded['center_bill']==bill, 'recorded baseline agrees')
        check(recorded['compensation_capacity']['h6_root_path']['max_additional_helpers']==capacity, 'recorded capacity agrees')
        rows.append(dict(baseline=name,target=target_name,kappa=str(k),capacity=capacity,
          stock=str(stock),deficit=deficit,center_bill=bill,
          pass_slack_scaled_1e24=oracle.display_interval(*pass_slack),
          fail_slack_scaled_1e24=oracle.display_interval(*fail_slack)))

paths = ['helper/charged_screen.py','helper/CHARGED-SCREEN.json','helper/README.md','invoice/verify.py']
source_hashes = {p: hashlib.sha256((PACKAGE/p).read_bytes()).hexdigest() for p in paths}
for p in ['research/niemeier-lattices/workbench/paid-controller/encoder_conservative.py',
          'research/niemeier-lattices/workbench/paid-controller/full_centers.py',
          'research/niemeier-lattices/workbench/paid-controller/banked.py',
          'research/niemeier-lattices/code/costs.py','certificates/selected-result.json']:
    source_hashes[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
output=dict(status='PASS_INDEPENDENT_L5_CHARGED_BOUNDARIES',rows=rows,
   source_hashes=source_hashes,assembly='Direct masses and ranks; no banked, costs or charged_screen import. Rational oracle imported from invoice/verify.py.',
   stock_replication_factor=Q,pad=PAD,child_cap=CAP,
   scope='Conditional complex invoice only; no scalar word, frame chronology, arbitrary-dirt restoration, compiler admission or bit-side envelope proved.')
(HERE/'RESULT.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
print(output['status'])
for row in rows:
    print(row['baseline'],row['target'],row['capacity'],
          'pass', float(F(row['pass_slack_scaled_1e24'][0],10**24)),
          'next', float(F(row['fail_slack_scaled_1e24'][1],10**24)))
