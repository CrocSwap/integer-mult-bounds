"""Exact all-size price ceiling for the admitted two-fragment root.

This reuses a pinned rational power-enclosure engine, not its historical
construction or invoices. No native/source replay or new kappa claim.
"""
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = HERE if (HERE/'two-fragment/RESULT.json').exists() else HERE/'release'
ENGINE = PACKAGE / 'runtime/root/research/higher-moment-strictification/verify.py'
assert sha256(ENGINE.read_bytes()).hexdigest() == '0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326'
spec = importlib.util.spec_from_file_location('allocation_interval_engine', ENGINE)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
K = Q('.0033072446849')
t = 1-K
ZERO = (Q(0), Q(0))

def add(*args):
    return sum(a[0] for a in args), sum(a[1] for a in args)

def neg(a):
    return -a[1], -a[0]

def scalar(a, c):
    return E.scale(a, Q(c))

def fixed(c):
    return Q(c), Q(c)

def h(n):
    return E.power(n,t)

def inc(n):
    return add(h(8*n+1),neg(h(8*n)))

def maximum(args):
    args = list(args)
    return max(a[0] for a in args), max(a[1] for a in args)

helpers = {1:14,2:8,3:4,4:108,5:16,6:3,7:9,8:40,9:361}
paid = {1:2231,2:454,3:490,4:109,5:152,6:8,7:9,8:1}
ell = scalar(add(E.moment(helpers,t), neg(E.moment(paid,t))),Q(1,104))
a = add(scalar(inc(2),2),fixed(-1))

# The relevant ordinary BIT stock caps kappa below .004. On this whole
# interval the native signed margin is strictly decreasing as well.
cap = Q('.004')
signed = {r:helpers.get(r,0)-paid.get(r,0) for r in set(helpers)|set(paid)}
ell_derivative = ZERO
for r,count in signed.items():
    powers = (E.power(r,1-cap)[0],h(r)[1])
    ell_derivative = add(ell_derivative,scalar(E.mul(powers,E.log_bounds(r)),Q(-count,104)))
assert ell_derivative[1]<0

def envelope(F):
    return add(scalar(ell,F),scalar(a,F-6),scalar(inc(1),4),h(8*F+1),scalar(h(4*F+1),2),fixed(-2))

def derivative(F):
    return add(ell,a,scalar(E.power(8*F+1,-K),8*t),scalar(E.power(4*F+1,-K),8*t))

tail_start = 50
B = envelope(tail_start)
D = derivative(tail_start)
assert B[1]<0 and D[1]<0

# Every full binary tree is represented by an ordered split at its root.
# The exact maximum is enclosed even when competing intervals overlap.
dp = [ZERO for _ in range(tail_start)]
for n in range(2,tail_start):
    dp[n] = add(maximum(add(dp[j],dp[n-j]) for j in range(1,n)),scalar(inc(n),2),fixed(-1))
X = [None for _ in range(tail_start)]
for n in range(3,tail_start):
    X[n] = maximum(add(dp[a],dp[b],dp[c],inc(b+c),inc(c))
                   for a in range(1,n-1)
                   for b in range(1,n-a)
                   for c in [n-a-b])

finite = {}
for F in range(6,tail_start):
    finite[F] = add(scalar(ell,F),h(8*F+1),fixed(-2),
                    maximum(add(X[x],X[F-x],h(8*x+1),h(8*(F-x)+1))
                            for x in range(3,F-2)))
    assert finite[F][1]<0, (F,E.display(finite[F]))

# Check that the formula specializes to the actual frozen literal invoice.
certificate_path = PACKAGE/'two-fragment/RESULT.json'
receipt = json.loads(certificate_path.read_bytes())
def find_invoice(x):
    if isinstance(x,dict):
        if x.get('status')=='PASS_TWO_PAID_FRAGMENTS_COMPLETE_PRICE':
            return x
        for v in x.values():
            found = find_invoice(v)
            if found is not None:return found
    return None
invoice = find_invoice(receipt)
assert invoice is not None
T = {int(r):n for r,n in invoice['targets'].items()}
P = {int(r):n for r,n in invoice['paid'].items()}
literal = scalar(add(E.moment(T,t),neg(E.moment(P,t))),Q(1,104))
actual = add(scalar(ell,18),scalar(dp[4],4),scalar(inc(5),2),scalar(inc(1),2),h(145),scalar(h(73),2),fixed(-2))
assert max(literal[0],actual[0])<=min(literal[1],actual[1])
# Authenticate the formula as an exact signed histogram, independently of
# numerical interval agreement or the choice of a power exponent.
formula = Counter({r:18*count for r,count in signed.items()})
for size,count in {2:8,4:4}.items():
    formula[8*size+1]+=208*count
    formula[8*size]-=208*count
    formula[1]-=104*count
for r,count in {145:104,73:208,41:208,40:-208,9:208,8:-208,1:-208}.items():
    formula[r]+=count
literal_signed=Counter(T)
literal_signed.subtract(P)
assert {r:n for r,n in formula.items() if n}=={r:n for r,n in literal_signed.items() if n}
# Four 4-leaf trees really attain the DP choices; no relaxed replacement.
balanced4=add(scalar(inc(2),4),scalar(inc(4),2),fixed(-3))
assert max(balanced4[0],dp[4][0])<=min(balanced4[1],dp[4][1])

best_F=max(finite,key=lambda F:finite[F][1])
result={
 'status':'PASS_EXACT_TWO_FRAGMENT_ALL_SIZE_RAW_CEILING',
 'raw_ceiling':str(K),
 'monotonicity_interval':[str(K),str(cap)],
 'native_margin_derivative':E.display(ell_derivative),
 'all_size_proof':'For F>=50, B(F)<=B(50)+(F-50)Bprime(50)<0 by concavity. F=6..49 are enclosed by exact interval dynamic programming over every binary split and positive six-child allocation.',
 'tail_start':tail_start,
 'tail_value':E.display(B),'tail_derivative':E.display(D),
 'finite_maximum_F':best_F,'finite_maximum_gap_per_port':E.display(finite[best_F]),
 'finite_gaps_per_port':{str(F):E.display(v) for F,v in finite.items()},
 'literal_formula_gap_per_port':E.display(actual),
 'literal_invoice_gap_per_port':E.display(literal),
 'exact_signed_histogram_matches':True,
 'source_sha256':sha256(certificate_path.read_bytes()).hexdigest(),
 'engine_sha256':sha256(ENGINE.read_bytes()).hexdigest(),
 'scope':'Fixed admitted two-pair root, central scalar source, six positive child sizes, arbitrary ordinary binary supplier trees, and the same two paid fragment orientations. The ceiling is proved through kappa=.004, beyond the retained ordinary BIT stock. No other root, source, retirement, or operator-valued control is excluded.',
 'disposition':'RETIRE allocation-only extensions of this exact root above the stated raw ceiling; the qualified conditional kappa remains 0.00330720.'
}
raw=json.dumps(result,indent=2)+'\n'
if sys.argv[1:]==['--write']:
    (HERE/'ALLOCATION-TAIL.json').write_text(raw)
else:
    assert sys.argv[1:]==[]
    assert (HERE/'ALLOCATION-TAIL.json').read_text()==raw,'Frozen all-size certificate'
print(result['status'],flush=True)
for key in ['tail_value','tail_derivative','finite_maximum_F','finite_maximum_gap_per_port']:
    print(key,result[key],flush=True)
