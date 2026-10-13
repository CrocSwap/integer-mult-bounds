"""Recompute the fine-grid outer refinement from a fresh strict replay."""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, importlib.util, json

if not __debug__:
    raise RuntimeError('The inherited outer engine requires assertions')
P = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--work', type=Path, required=True)
work = ap.parse_args().work.resolve()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old_source = (P/'comparison/PR615-assemble.py').read_text()
expected_source = old_source.replace(
    'ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)',
    'ticks=margin*10**24;k=Q((ticks.numerator-1)//ticks.denominator,10**24)'
).replace("('next_grid',k+Q(1,10**18),eta,beta)",
          "('next_grid',k+Q(1,10**24),eta,beta)")
assert expected_source != old_source
assert expected_source == (P/'code/assemble.py').read_text()
engine = P/'vendor/multicold/engines/outer.py'
spec = importlib.util.spec_from_file_location('fixed_outer', engine)
outer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(outer)
old, new = read(P/'comparison/PR615-ASSEMBLY.json'), read(work/'ASSEMBLY.json')
assert old['complex_profile'] == new['complex_profile']
assert old['provider_counts'] == new['provider_counts']
rows = []
for prefix in ('', 'conservative_'):
    b = Q(old[prefix+'complex_lower'])
    assert b == Q(new[prefix+'complex_lower'])
    c = Q(old['bit_lower'])
    assert c == Q(new['bit_lower'])
    eta = beta = Q(1,10**24)
    s = min(c,(1-beta)*b)-Q(1,10**27)
    assert 0 < s < c and s < (1-beta)*b
    a = Q(384599,10**10)
    cuts = []
    for _ in range(7):
        previous = a
        a = (1-s)*s+s*previous
        gap = min(s-a,1-a-s,1-a-s*(1-previous),1-s)
        assert previous < a < s < 1-a and gap > 0
        ceil = lambda t: -(-t.numerator//t.denominator)
        cutoff = max(ceil(36/gap**2),ceil(2*(4+512)/gap))
        assert cutoff*gap**2 >= 36 and cutoff*gap >= 2*(4+512)
        cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cutoff)))
    assert cuts == old[prefix+'bootstrap'] == new[prefix+'bootstrap']
    q = a*(1-2*eta)
    margin = (1-eta)*q/(1+q)
    k, oldk = Q(new[prefix+'kappa']), Q(old[prefix+'kappa'])
    assert oldk < k < margin < k+Q(1,10**24)
    bridge = {'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},
              'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
    z = outer.assembly(a,b,bridge,k,eta=eta,beta=beta)
    assert len(z['strict_constraints']) == 47
    assert all(x > 0 for x in z['strict_constraints'].values())
    assert {n:str(v) for n,v in z['strict_constraints'].items()} == new[prefix+'outer']
    rejected = []
    for name,kk,ee,be in [('next_fine_grid',k+Q(1,10**24),eta,beta),
                           ('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),
                           ('unit_beta',k,eta,Q(1))]:
        try:
            outer.assembly(a,b,bridge,kk,eta=ee,beta=be)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    rows.append(dict(model=prefix or 'native',baseline=str(oldk),candidate=str(k),
                     gain=str(k-oldk),minimum_margin=str(margin),
                     absorption_gap=str(margin-k),strict_constraints=47,
                     negative_controls_rejected=rejected))
record = dict(status='PASS_EXACT_FINE_GRID_REFINEMENT',rows=rows,
              outer_engine_sha256=sha(engine),scope=old['scope'])
(work/'REFINEMENT-CERTIFICATE.json').write_text(json.dumps(record,indent=2)+'\n')
print(record['status'],rows[0]['candidate'],flush=True)
