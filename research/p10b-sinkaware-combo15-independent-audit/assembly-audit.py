"""Independent closed-form recurrence and strict rational outer-grid audit.
No imports from the construction's arithmetic implementation.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('proof',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
raw=(args.proof/'REFINEMENT.json').read_bytes();r=json.loads(raw)
price=json.loads((args.proof/'PRICE.json').read_text())
eta,beta=F(r['eta']),F(r['beta']);grid=r['grid'];s=F(r['ordinary_saving']['value'])
b=F(price['complex_saving']);assert b==F(r['complex_saving'])
limit=(1-beta)*b
strict_ticks=(limit.numerator*grid-1)//limit.denominator
strict_cap=F(strict_ticks,grid)
assert strict_cap==F(r['ordinary_saving']['strict_complex_cap'])
assert s==min(F(r['root']['lower']),strict_cap)<limit
start=F(r['bootstrap']['initial']);levels=r['bootstrap']['levels'];C=r['complete_literal_invoice']['coefficient']
def bound(value):
    q=value*(1-2*eta)
    return (1-eta)*q/(1+q)
def strict_grid(value):
    q=bound(value)
    return F((q.numerator*grid-1)//q.denominator,grid)
cap=strict_grid(s)
assert cap==F(r['kappa'])
for level,actual in enumerate(r['bootstrap']['chain']):
    # Solve x_(n+1)=s(1-s)+s*x_n exactly without using iteration.
    closed=s-(s-start)*s**level
    assert closed==F(actual)
    if level:
        row=r['bootstrap']['gaps'][level-1]
        previous=s-(s-start)*s**(level-1)
        gaps={'atom':s-closed,'borrowing':1-closed-s,'remainder':1-closed-s*(1-previous),'stock':1-s}
        assert gaps=={k:F(v) for k,v in row['gaps'].items()}
        delta=min(gaps.values());cut=row['primitive_coefficient_cutoff_log2']
        assert delta>0 and cut*delta**2>=36 and cut*delta>=2*(4+(C-1).bit_length())
        if level<levels:assert strict_grid(closed)<cap
leaf=s-(s-start)*s**levels
assert strict_grid(leaf)==cap
assert cap<bound(leaf)<=bound(s)<=cap+F(1,grid)
assert F(r['assembly']['minimum_margin'])==bound(leaf)
q=leaf*(1-2*eta);eps=(1-eta)/(1+q)
independent_margins={'balanced_prefix':1-eps,'coordinate_movement':leaf,'compact_phase_layer':eps*q,'bulk_exposure':leaf,'Gaussian_arithmetic':min(1-eps-eta/8,(eps*q+1-eps)/2-eta/8),'scalar_work':1-eps-eta/8,'dimension':eps}
assert independent_margins=={k:F(v)for k,v in r['assembly']['margins'].items()}
assert min(independent_margins.values())>cap
assert len(r['assembly']['strict_constraints'])==47 and all(F(v)>0 for v in r['assembly']['strict_constraints'].values())
result=dict(status='PASS_INDEPENDENT_CLOSED_FORM_BOOTSTRAP_COMPLEX_CLIPPING_AND_OUTER_GRID',kappa=str(cap),complex_b=str(b),ordinary_saving=str(s),bootstrap_levels=levels,refinement_sha256=hashlib.sha256(raw).hexdigest(),scope='Independently recomputed all finite recurrence levels by closed form, their cutoffs, strict complex cap, seven outer margins and final grid; full structural and moment admission remain the complete verifier responsibility.')
assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],str(cap))
