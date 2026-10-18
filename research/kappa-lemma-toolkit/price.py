"""Fresh owner recount, two exact moments and unchanged 47-row outer assembly."""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
import json, gzip, hashlib, importlib.util, argparse
import sys
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parent
campaign = root.parent / 'selective-borrowing-kappa'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, help='Optional external receipt file')
args = parser.parse_args()
if args.out and (args.out.resolve().is_relative_to(campaign.resolve()) or args.out.resolve().is_relative_to(root.resolve())):
    raise ValueError('--out must be outside the published package')
for pin in json.loads((campaign / 'arithmetic/SOURCES.json').read_bytes())['files']:
    if hashlib.sha256((campaign / 'arithmetic' / pin['path']).read_bytes()).hexdigest() != pin['sha256']:
        raise ValueError('arithmetic vendor source drift')
base = campaign / 'owners/inputs'
plan = json.loads((base / 'PLAN.json').read_bytes())
owners_path = root / 'OWNERS.json.gz'
audit_path = root / 'OWNERS-EXPECTED.json'
trace_path = campaign / 'local/data/forward.json'
trace = json.loads(trace_path.read_bytes())
rows = json.loads(gzip.decompress(owners_path.read_bytes()))
bycall = defaultdict(list)
bybin = defaultdict(list)
widths = {int(k): v for k, v in trace['helper_widths'].items()}
for r in rows:
    if not r['copy'] == 112 * r['owner_replica'] + r['port']:
        raise ValueError('exact arithmetic admission failed')
    if not r['width'] == widths[r['helper']]:
        raise ValueError('exact arithmetic admission failed')
    if not plan['order'][r['time']] == [r['stage'], r['replica']]:
        raise ValueError('exact arithmetic admission failed')
    if not r['time'] in plan['windows'][f"{r['owner_replica']},{r['child']}"][1]:
        raise ValueError('exact arithmetic admission failed')
    bycall[r['time']].append(r)
    bybin[r['owner_replica'], r['child'], r['port']].append(r)
if not (len(bycall) == 72 and len(rows) == 72 * 436):
    raise ValueError('exact arithmetic admission failed')
for rr in bycall.values():
    if not {r['helper'] for r in rr} == set(widths):
        raise ValueError('exact arithmetic admission failed')
    if not len({r['family'] for r in rr}) == len(rr):
        raise ValueError('exact arithmetic admission failed')
occupied = Counter()
for k, rr in bybin.items():
    cap = plan['windows'][f'{k[0]},{k[1]}'][0]
    used = set()
    for r in rr:
        axes = set(range(r['offset'], r['offset'] + r['width']))
        if not (axes and min(axes) >= 0 and (max(axes) < cap) and (not used & axes)):
            raise ValueError('exact arithmetic admission failed')
        used |= axes
    occupied[k] = len(used)
H = Counter()
for wc, (cap, times) in plan['windows'].items():
    rep, ch = map(int, wc.split(','))
    for port in range(112):
        rem = cap - occupied[rep, ch, port]
        if not rem >= 0:
            raise ValueError('exact arithmetic admission failed')
        if rem:
            H[rem] += 1
for r, n in trace['local_profile'].items():
    H[int(r)] += 72 * n
W = plan['live']
m = 73
mass = sum((r * n for r, n in H.items()))
if not (mass == 520704 and m * W - mass == 2560):
    raise ValueError('exact arithmetic admission failed')
if not m * m > 2 * max(H) ** 2:
    raise ValueError('exact arithmetic admission failed')

def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod
eng = campaign / 'arithmetic/vendor'
M = load('exact_mercator', eng / 'moment.py')
B = load('independent_atanh', eng / 'base_two_moment.py')
B.log_bounds = lru_cache(None)(B.log_bounds)
outer_path = eng / 'outer.py'
A = load('retained_outer', outer_path)
_retained_assembly = A.assembly
def checked_assembly(*positional, **keywords):
    result = _retained_assembly(*positional, **keywords)
    if len(result['strict_constraints']) != 47 or len(result['margins']) != 7:
        raise ValueError('retained strict row inventory changed')
    if min(result['strict_constraints'].values()) <= 0:
        raise AssertionError('nonpositive strict outer row')
    if result['minimum_margin'] != min(result['margins'].values()):
        raise ValueError('wrong minimum margin')
    return result
A.assembly = checked_assembly

bit_path = eng / 'BIT-EXPECTED.json'
bit = json.loads(bit_path.read_bytes())
bt = bit['nine']
BH = {int(r): n for r, n in bt['profile'].items()}
BW = bt['bit']['live']
c = Q(bt['bit_lower'])
b = Q(168358, 10 ** 8)
k = Q(168074, 10 ** 8)
if not 64 * BW - sum((r * n for r, n in BH.items())) == 32 * (8 * bit['word']['v'] - 9 * sum(bit['word']['copy_ranks'])):
    raise ValueError('exact arithmetic admission failed')
moments = []

def check(name, h, m, w, z, bad):
    x = M.moment(h, m, w, z, bad)
    y = B.moment(m, w, list(h.items()), z)
    if bad:
        v = B.moment(m, w, [(1, 32 * m * m * sum(h.values()))], z)
        y = (y[0] + v[0] / 10 ** 16, y[1] + v[1] / 10 ** 16)
    if not (x[1] < 1 and y[1] < 1):
        raise ValueError((name, x, y))
    moments.append({'side': name, 'saving': str(z), 'surcharge': bad, 'mercator_residual': [str(v - 1) for v in x], 'atanh_residual': [str(v - 1) for v in y]})
check('complex_native', H, 73, W, b, False)
check('complex_conservative', H, 73, W, b, True)
check('bit_retained', BH, 64, BW, c, True)
eta = beta = Q(1, 10 ** 8)
s = min(c, (1 - beta) * b) - Q(1, 10 ** 11)
chain = [Q(384599, 10 ** 10)]
cuts = []

def ceil(q):
    return -(-q.numerator // q.denominator)
for _ in range(7):
    old = chain[-1]
    a = (1 - s) * s + s * old
    gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
    if not (old < a < s < c and s < (1 - beta) * b and (0 < gap)):
        raise ValueError('exact arithmetic admission failed')
    cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + 512) / gap))
    if not (cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + 512)):
        raise ValueError('exact arithmetic admission failed')
    chain.append(a)
    cuts.append({'saving': str(a), 'gap': str(gap), 'example_constant_bits':512,'example_cutoff_log2': str(cutoff),'universal_cutoff_recipe':'For each sequential fixed C choose integer ell with C < 2^ell; L=max(ceil(36/gap^2),ceil(2*(4+ell)/gap)). These example cutoffs do not bound the actual inherited constants.'})
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
assembly = A.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
if not (len(assembly['strict_constraints']) == 47 and min(assembly['strict_constraints'].values()) > 0):
    raise ValueError('exact arithmetic admission failed')
controls = []
for name, kk, ee, bb in [('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1)), ('above_balance', assembly['minimum_margin'] + Q(1, 10 ** 12), eta, beta)]:
    try:
        A.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
    except (AssertionError, ZeroDivisionError):
        controls.append(name)
    else:
        raise ValueError(('control accepted', name))
if not M.moment(H, 73, W, b + Q(1, 10 ** 5), False)[0] > 1:
    raise ValueError('exact arithmetic admission failed')
controls.append('supplier_endpoint_too_large')
previous = Q(3361,2000000)
if not k > previous + Q(1, 10 ** 7):
    raise ValueError('exact arithmetic admission failed')

def dec(q):
    with localcontext() as cx:
        cx.prec = 55
        return str(Decimal(q.numerator) / Decimal(q.denominator))
source_paths = [owners_path, audit_path, trace_path, base / 'PLAN.json', eng / 'moment.py', eng / 'base_two_moment.py', outer_path, bit_path]
result = {'status': 'PASS_RECOUNT_TWO_EXACT_MOMENTS_AND_47_STRICT_OUTER', 'kappa': str(k), 'kappa_decimal': dec(k), 'certified_complex_saving': str(b), 'inherited_bit_saving': str(c), 'increase_over_previous_open_claim': dec(k - previous), 'relative_increase_percent': dec(100 * (k / previous - 1)), 'calls': 72, 'helpers_per_call': 436, 'live': W, 'profile': dict(sorted(H.items())), 'rank_mass': mass, 'deficit': 2560, 'moments': moments, 'bootstrap': cuts, 'outer_parameters': assembly['parameters'], 'outer_constraints': {n: str(v) for n, v in assembly['strict_constraints'].items()}, 'controls_rejected': controls, 'source_sha256': {p.relative_to(root.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}, 'scope': 'Exact finite recount and retained conditional outer arithmetic only. Requires independently source-bound native word, physical owner charts/controller, full work/precision/stock invoice and original all-size/analytic/bit assumptions; not full Lean multiplication proof.'}
if args.out:
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, default=str) + '\n')
print(json.dumps({k: v for k, v in result.items() if k in ['status', 'kappa', 'kappa_decimal', 'certified_complex_saving', 'increase_over_previous_open_claim', 'relative_increase_percent', 'profile', 'controls_rejected']}))
