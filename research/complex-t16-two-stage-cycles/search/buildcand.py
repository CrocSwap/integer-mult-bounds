"""Build OWNERS/PLAN/SPEC for a candidate owner map from the selected PR1094 package (2077-style).
argv: LIBDIR OWNERS_IN OUTDIR [sigmas]"""
import sys, json, gzip, hashlib
sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter
from pathlib import Path
rows = lib.read(sys.argv[2]); out = Path(sys.argv[3]); out.mkdir(parents=True)
canon = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':')).encode()
dg = lambda b: hashlib.sha256(b).hexdigest()
au = lib.audit(rows)
plan = json.loads((lib.SEL/'PLAN.json').read_text()); spec = json.loads((lib.SEL/'SPEC.json').read_text())
container = gzip.compress(json.dumps(rows).encode(), mtime=0)
assert json.loads(gzip.decompress(container)) == rows
profile = {str(k): v for k, v in sorted(au['profile'].items())}
plan.update(profile=profile, assignment_sha256=dg(container), assignment_content_sha256=dg(canon(rows)))
plan['replica_lift']['owners_file_sha256'] = dg(container)
plan_bytes = (json.dumps(plan, indent=2) + '\n').encode()
pn, pc = lib.price(au['profile']), lib.price(au['profile'], True)
spec['data'] = dict(owners_sha256=dg(container), plan_sha256=dg(plan_bytes))
e = spec['expected']
from decimal import Decimal, localcontext
from fractions import Fraction as Q
def dec(x):
    x = Q(x)
    with localcontext() as ctx: ctx.prec = 70; return str(Decimal(x.numerator) / Decimal(x.denominator))
e.update(complex_lower=pn['endpoint'], conservative_complex_lower=pc['endpoint'], kappa=pn['kappa'], kappa_decimal=dec(pn['kappa']),
         conservative_kappa_decimal=dec(pc['kappa']), cross_replica_helper_roles=au['cross_replica_roles'],
         idle_remainders=sum(au['idle'].values()), idle_remainder_profile={str(k): v for k, v in sorted(au['idle'].items())}, global_profile=profile)
if len(sys.argv) > 4: e['actual_73column_sigmas'] = int(sys.argv[4])
(out/'OWNERS.json.gz').write_bytes(container); (out/'PLAN.json').write_bytes(plan_bytes)
(out/'SPEC.json').write_text(json.dumps(spec, indent=2) + '\n')
print('built', out, pn['kappa_decimal'], pc['kappa_decimal'], au['idle'])
