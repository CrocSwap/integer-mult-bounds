"""Re-enumerate every pattern and certify the fixed-inventory dual.

Derived from the separate review_budget.py by Ross Richardson with substantial
OpenAI Codex assistance; see ADAPTATIONS.json. No optimizer or cached PASS input.
The source-bound positive-binomial engine is credited to PR3531.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse, hashlib, json, types
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--predecessor', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
binomial_source = (a.predecessor / 'vendor/pr3531/binomial.py').read_bytes()
if hashlib.sha256(binomial_source).hexdigest() != '03eebf2be23cab07e5f9e978980fee7b17e10847da5720c3e4e0adb243e8e4fa':
    raise ValueError('source-bound binomial engine')
B = types.ModuleType('positive_binomial_dual')
exec(compile(binomial_source, 'PR3531/binomial.py', 'exec'), B.__dict__)
M, T, W = (73, 740, 663040)
CAPS = (8, 16, 32, 48)
WIDTHS = (4, 5, 6, 7, 8, 9)
CAP_TOTAL = (672, 448, 448, 448)
INVENTORY = (26, 2, 18, 52, 97, 213)
H0 = {1: 16417896, 2: 4835160, 3: 1540174, 4: 679321, 5: 143992, 6: 3, 8: 53280, 48: 283185}
HA = {1: 16417892, 2: 4835160, 3: 1540174, 4: 679320, 5: 143993, 7: 3, 8: 53280, 48: 283185}
DELTA = {1: -4, 4: -1, 5: 1, 6: -3, 7: 3}
L = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
C0 = Q('0.001730006549538841847005')
CA = Q('0.001730006690311348872326')
LO = Q('0.001730096363528623534230')
HI = LO + Q(1, 10 ** 24)

def solve(a, b):
    n = len(a)
    z = [[Q(v) for v in row] + [Q(b[i])] for i, row in enumerate(a)]
    for j in range(n):
        k = next((k for k in range(j, n) if z[k][j]))
        z[j], z[k] = (z[k], z[j])
        q = z[j][j]
        z[j] = [x / q for x in z[j]]
        for k in range(n):
            if k != j:
                q = z[k][j]
                z[k] = [x - q * y for x, y in zip(z[k], z[j])]
    return [row[-1] for row in z]
patterns = []
for capacity in CAPS:
    for counts in product(*(range(capacity // width + 1) for width in WIDTHS)):
        used = sum((n * w for n, w in zip(counts, WIDTHS)))
        if used <= capacity:
            patterns.append((capacity, counts, capacity - used))
if not len(patterns) == len(set(patterns)) == 2551:
    raise ValueError('dual condition: len(patterns) == len(set(patterns)) == 2551')
column = lambda p: [Q(p[0] == capacity) for capacity in CAPS] + list(map(Q, p[1]))
specs = [(8, (8,), Q(672)), (16, (7, 9), Q(448)), (32, (9, 9, 9), Q(57, 4)), (32, (7, 8, 8, 9), Q(39, 2)), (32, (7, 7, 9, 9), Q(1, 4)), (32, (6, 8, 9, 9), Q(162)), (32, (5, 9, 9, 9), Q(18)), (32, (4, 9, 9, 9), Q(234)), (48, (), Q(1531, 4)), (48, (9, 9, 9, 9, 9), Q(261, 4))]
basis = [(cap, tuple((ws.count(w) for w in WIDTHS)), cap - sum(ws)) for cap, ws, n in specs]
amount = [n for cap, ws, n in specs]
if not all((p in patterns for p in basis)):
    raise ValueError('dual condition: all((p in patterns for p in basis))')
columns = [column(p) for p in basis]
A = list(map(list, zip(*columns)))
rhs = list(map(Q, CAP_TOTAL)) + [Q(9 * n) for n in INVENTORY]
if not [sum((a * n for a, n in zip(row, amount))) for row in A] == rhs:
    raise ValueError('dual condition: [sum((a * n for a, n in zip(row, amount))) for row in A] == rhs')
if not (solve(A, rhs) == amount and all((n > 0 for n in amount))):
    raise ValueError('dual condition: solve(A, rhs) == amount and all((n > 0 for n in amount))')
ideal_idle = Counter()
for p, n in zip(basis, amount):
    if p[2]:
        ideal_idle[p[2]] += n * T
ideal = Counter({r: 9 * T * n for r, n in L.items()})
ideal.update(ideal_idle)
if not all((Q(n).denominator == 1 for n in ideal.values())):
    raise ValueError('dual condition: all((Q(n).denominator == 1 for n in ideal.values()))')
ideal = {r: int(n) for r, n in ideal.items()}
if not sum((r * n for r, n in ideal.items())) == sum((r * n for r, n in HA.items())) == 65088 * T:
    raise ValueError('dual condition: sum((r * n for r, n in ideal.items())) == sum((r * n for r, n in HA.items())) == 65088 * T')
root_enclosures = {}
for name, profile, lo, hi in [('predecessor', H0, C0, C0 + Q(1, 10 ** 24)), ('candidate_A', HA, CA, CA + Q(1, 10 ** 24)), ('relaxed_ceiling', dict(ideal), LO, HI)]:
    below = B.moment(profile, lo, W)
    above = B.moment(profile, hi, W)
    if not below[1] < 1 < above[0]:
        raise ValueError('dual condition: below[1] < 1 < above[0]')
    root_enclosures[name] = {'lower': str(lo), 'upper': str(hi), 'moment_at_lower': list(map(str, below)), 'moment_at_upper': list(map(str, above))}
cache = {}

def f(rank, b):
    if rank == 0:
        return (Q(0), Q(0))
    if (rank, b) not in cache:
        cache[rank, b] = tuple((73 * x for x in B.moment({rank: 1}, b, 1)))
    return cache[rank, b]
dual_symbolic = [solve(list(map(list, zip(*A))), [int(i == j) for i in range(10)]) for j in range(10)]

def coefficients(p):
    a = column(p)
    out = Counter({p[2]: Q(1)}) if p[2] else Counter()
    for j, bp in enumerate(basis):
        if bp[2]:
            out[bp[2]] -= sum((x * y for x, y in zip(a, dual_symbolic[j])))
    return {r: n for r, n in out.items() if n}
tight = []
strict = []
coefficient_hash = hashlib.sha256()
for p in patterns:
    coeff = coefficients(p)
    coefficient_hash.update(json.dumps([p, sorted(((r, str(n)) for r, n in coeff.items()))], separators=(',', ':')).encode())
    if not coeff:
        tight.append(p)
        continue
    lower = sum((n * f(r, LO if n > 0 else HI)[0 if n > 0 else 1] for r, n in coeff.items()))
    if not lower > 0:
        raise ValueError('dual condition: lower > 0')
    strict.append((lower, p))
if not (len(tight), len(strict)) == (12, 2539):
    raise ValueError('dual condition: (len(tight), len(strict)) == (12, 2539)')
result = dict(status='PASS_ALL_2551_FIXED_INVENTORY_PATTERNS', patterns=len(patterns), strict=len(strict), symbolically_zero=len(tight), coefficient_sha256=coefficient_hash.hexdigest(), root_enclosures=root_enclosures, ideal_profile=ideal, min_reduced_cost_lower=str(min(strict)[0]), scope='Finite exhaustive dual plus written scaling proof for every positive integer T with the same capacities, width inventory, local bill and live stock896T; no chronological attainment or global optimum.')
a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
print(result['status'])
