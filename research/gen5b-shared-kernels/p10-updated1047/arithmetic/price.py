"""Recompute the new baseline and exactly price the single admitted matching delta."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions();support.verify_inputs();support.verify_dependencies()
import reproduce_p10 as b
import price_candidate as p
baseline=b.run();p.baseline=lambda:baseline
support.out('arithmetic','baseline-receipt.json').write_text(json.dumps(b.ae.serial(baseline),indent=2)+'\n')
d=json.loads(support.out('matching','weighted890-delta.json').read_text())
result=p.price(d['histogram_delta'],d['residual_delta'],label='Weighted 890 on the immutable 1047-kernel baseline')
assert result['assembly']['kappa']==b.F(769997773182046,10**18)
assert baseline['assembly']['kappa']==b.F(769553898621543,10**18)
support.out('arithmetic','weighted890-price.json').write_text(json.dumps(b.ae.serial(result),indent=2)+'\n')
report=dict(status='PASS_SOURCE_BOUND_WEIGHTED890_ARITHMETIC',head=support.HEAD,word_sha256=support.WORD_SHA,baseline_kappa=baseline['assembly']['kappa'],candidate_kappa=result['assembly']['kappa'],improvement_percent=result['improvement_percent'],literal_stock=result['literal_stock'],banked_calls=result['banked_calls'],banked_rank_mass=result['banked_rank_mass'],strict_constraints=result['assembly']['strict_constraint_count'],root_lower=result['bit_root_bracket']['lower'],root_upper=result['bit_root_bracket']['upper'],scope='Exact conditional arithmetic; physical admission and finite interfaces are separately bound.')
report['source_sha256']={name:support.sha(support.HERE/name) for name in ('arithmetic/price.py','arithmetic/reproduce_p10.py','arithmetic/price_candidate.py','support.py')}
support.out('arithmetic','arithmetic-result.json').write_text(json.dumps(b.ae.serial(report),indent=2)+'\n');print(json.dumps(b.ae.serial(report),indent=2))
