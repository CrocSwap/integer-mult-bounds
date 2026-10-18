"""Join finite changed-source admissions; does not prove inherited all-size contracts.
Prepared with OpenAI Codex assistance. Inherits upstream PR376/377/390 notices.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json,gzip,sys
sys.dont_write_bytecode=True
p=Path(sys.argv[1]);read=lambda q:json.loads(Path(q).read_text());digest=lambda q:sha256(Path(q).read_bytes()).hexdigest()
r=read(p/'RESULT.json');a=read(p/'CLIFFORD-REVIEW.json')
assert r['status']=='PASS_CHANGED_LOCAL_FRAMES_DIRTY_WORDS_BANKS_TWO_MOMENTS_AND_FINITE_INVOICE'
assert a['status']=='PASS_EXACT_GAUSSIAN_CLIFFORD_LOCAL_FRAMES_AND_CHILDREN'
assert a['certificate_sha256']==r['candidate_certificate_sha256']
assert a['all_child_equalities_include_global_phase'] and a['endpoint_adapters']==240
assert digest(p/'CLIFFORD-RECIPES.json')==a['recipe_sha256']
assert sha256(gzip.decompress((p/'CHANGED-TEMPLATE.json.gz').read_bytes())).hexdigest()==r['template_sha256']
assert digest(p/'FROZEN-RESPONSE.json')==r['frozen_response_literal_sha256']
assert all(digest(q)==s for q,s in r['source_hashes'].items())
assert all(z['independent_live_columns']==240+r['R'] and z['private_restored_zero'] for z in r['scalar_rows'].values())
assert all(len(z['mutation_controls'])==7 and all(c['rejected'] for c in z['mutation_controls']) for z in r['local_splice'].values())
H={int(k):n for k,n in r['profile'].items()};assert sum(H.values())==r['paid_calls'] and sum(k*n for k,n in H.items())==r['rank_mass']
assert r['m']*r['live']-r['rank_mass']==r['deficit']==2496
inv=r['invoice'];assert inv['router_bits']<inv['G_exponent'] and inv['literal_bits']<inv['E_exponent'] and inv['required_C0_bits']<inv['C0_exponent']
assert inv['physical_row_coefficient']<inv['retained_row_coefficient']==20161
assert inv['halving_integer_inequality'][0]>inv['halving_integer_inequality'][1] and inv['induction_gap_multiple_B']==49
mb=r['moment_bounds'];assert Q(mb['first_lower'][1])<1<Q(mb['first_upper'][0]) and Q(mb['second_lower_upper'])<1<Q(mb['second_upper_lower'])
bridge=dict(proof='Finite source-counted changed invocation invoice; inherited all-size theorem interfaces remain conditional',representation='Exact powers and explicit overcharge for changed source',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=str(Q(10**6)-Q(51*20161,25))))
source=dict(result_sha256=digest(p/'RESULT.json'),clifford_review_sha256=digest(p/'CLIFFORD-REVIEW.json'),join_script_sha256=digest(Path(__file__)))
z=dict(status='PASS_FINITE_CHANGED_TARGET_READ_ADMISSION',candidate_certificate_sha256=r['candidate_certificate_sha256'],baseline_certificate_sha256=r['baseline_certificate_sha256'],profile=r['profile'],m=r['m'],stock=r['live'],physical=r['physical'],paid_calls=r['paid_calls'],complex_coarse=r['coarse'],moment_bounds=mb,finite_invoice=inv,bridge=bridge,dirty_response_extension=r['dirty_response_extension'],source_receipts=source,scope='Finite fixed-E8 changed-source admission only. Fresh dirty-column, literal primitive, frame/phase, histogram, work-lifetime, negative-control, conservative finite bill and two-rational-moment checks passed. Conditional sufficiency retains inherited compressed-window, arbitrary-bank correlated-dirt, local/compiler, precision, analytic, restored-row and ordinary-wrapper theorem interfaces. No Lean or independent all-size root proof is claimed.')
out=p/'JOINED-ADMISSION.json';assert not out.exists();out.write_text(json.dumps(z,indent=2)+'\n');print(z['status'],z['complex_coarse'])
