"""Independent re-check of a gauge44 FULL-WORD (written for PR869's U8 word).

Shares no code with audit_local.py and uses different methods:
- scalar map: dense matrices mod 16 primes (~2^496) plus a rigorous magnitude/2-adic height bound, so residues
  determine every entry exactly (the run prints the certified height);
- compensation: solved as Rest^-1 * E * Pre^-1 instead of propagated from dirt;
- frames: subspaces of F2^h held as 2^h-bit membership sets instead of reduced bases.
Usage: xcheck.py FULL-WORD.json.gz [expected-profile-json]
"""
import gzip, json, sys
from collections import Counter
from fractions import Fraction
import numpy as np
from math import prod
from sympy import prevprime
from sympy.ntheory.modular import crt

P = [2**31 - 1]
while len(P) < 16:
    P.append(prevprime(P[-1]))
PP = np.array(P, dtype=np.int64)[:, None]
MOD = prod(P)


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


def residues(q):
    return np.array([q.numerator * pow(q.denominator, -1, p) % p for p in P], dtype=np.int64)[:, None]


class Mat:
    """n x n dyadic matrix: residues mod 16 primes, plus an |entry| bound and a 2-adic denominator per row."""
    def __init__(self, n):
        self.r = np.broadcast_to(np.eye(n, dtype=np.int64), (len(P), n, n)).copy()
        self.bound = np.eye(n)
        self.den = np.zeros(n, dtype=np.int64)

    def addrow(self, t, s, q):  # row t += q * row s
        e = q.denominator.bit_length() - 1
        require(q.denominator == 1 << e, 'non-dyadic scalar')
        self.r[:, t] = (self.r[:, t] + residues(q) * self.r[:, s]) % PP
        self.bound[t] = (self.bound[t] + abs(float(q)) * self.bound[s]) * (1 + 1e-12)
        self.den[t] = max(self.den[t], self.den[s] + e)

    def scalerow(self, t, q):
        require(q != 0 and q.denominator & (q.denominator - 1) == 0 and abs(q.numerator) & (abs(q.numerator) - 1) == 0, 'non-unit dyadic scale')
        self.r[:, t] = self.r[:, t] * residues(q) % PP
        self.bound[t] *= abs(float(q))
        self.den[t] += max(0, q.denominator.bit_length() - 1)

    def apply(self, g, inverse=False):
        q = Fraction(g[3], g[4]) if g[0] == 'add' else Fraction(g[2], g[3])
        if g[0] == 'add':
            require(g[1] != g[2], 'self add')
            self.addrow(g[1], g[2], -q if inverse else q)
        else:
            self.scalerow(g[1], 1 / q if inverse else q)

    def certify(self):
        """Every numerator N = entry * 2^den[row] satisfies |N| < MOD/2, so residues determine entries exactly."""
        worst = float((self.bound * 2.0 ** self.den[:, None]).max())
        require(worst < 2.0 ** (MOD.bit_length() - 3), 'bound too large for exact CRT')
        return worst

    def entry(self, i, j):
        """Exact rational entry (i, j) by CRT."""
        d = 1 << int(self.den[i])
        x = int(crt(P, [int(a) for a in self.r[:, i, j]])[0]) * d % MOD
        return Fraction(x - MOD if x > MOD // 2 else x, d)


def nonzero(m, minus_identity=False):
    print(f'certified height < 2^{np.log2(m.certify()):.1f} < MOD/8 = 2^{MOD.bit_length() - 4}')
    r = m.r - np.eye(N, dtype=np.int64) if minus_identity else m.r
    return (r != 0).any(axis=0)


def product(gates, inverse=False):
    m = Mat(N)
    for g in (reversed(gates) if inverse else gates):
        m.apply(g, inverse)
    return m


def span(gens):
    s = {0}
    for g in gens:
        s |= {x ^ g for x in s}
    return sum(1 << x for x in s)


def rank(mask):
    return mask.bit_count().bit_length() - 1


w = json.loads(gzip.open(sys.argv[1]).read())
h, v = w['report']['h'], w['report']['v']
require(len(w['ports']) == v, 'port count')
R = w['report']['R']
N = 2 * v + R
require(all(0 <= q < N for k in ('A', 'cut', 'B', 'precondition', 'cleanup') for g in w[k] for q in (g[1:3] if g[0] == 'add' else g[1:2])), 'register out of range')
targets, helpers = range(v, 2 * v), range(2 * v, N)
entering = {int(q) for q in w['start_extra']}
lowends = {int(q) for q in w['helper_final']}
regs = lambda g: g[1:3] if g[0] == 'add' else g[1:2]

# 1. Reads: no gate outside the target block reads a target in A/B.
require(all(not (v <= g[2] < 2 * v) for g in w['A'] + w['B'] if g[0] == 'add' and not v <= g[1] < 2 * v), 'non-target reads target')

# 2. Scalar map, with compensation solved rather than propagated.
early = dict((i, U) for i, U in w['early_cleanup'])
require(len(early) == len(w['early_cleanup']), 'duplicate early cleanup')
tail = [w['cleanup'][i][:-1] + [U] for i, U in w['early_cleanup']]
clean = [g for i, g in enumerate(w['cleanup']) if i not in early]
main = w['A'] + w['cut'] + w['B']
rest = main + tail + clean
# comp = rest^-1 * E * pre^-1, where E adds source t into target v+t.
comp = product(w['precondition'], inverse=True)
for t in range(v):
    comp.addrow(v + t, t, Fraction(1))
for g in reversed(rest):
    comp.apply(g, inverse=True)
nz = nonzero(comp, minus_identity=True)
block = np.zeros((N, N), dtype=bool)
block[np.ix_(targets, helpers)] = True
require(not nz[~block].any(), 'compensation is not a target<-helper block')
pairs = list(zip(*np.nonzero(nz)))
used = {int(k) for _, k in pairs}
require(not set(used) & entering, 'nonzero entrance response')
require(not set(used) & lowends, 'compensation touches a low end')
require(not any(set(regs(g)) & (entering | lowends) for g in w['precondition']), 'precondition touches residual helper')
require(all(g[-1] == [] for g in w['precondition']), 'framed precondition')
print('scalar map exact; solved compensation has', len(pairs), 'entries on', len(used), 'helpers')

# 3. Frames and paid profile.
full = span([1 << i for i in range(h)])
cur = [span([p]) for p in w['ports']] + [span([])] * (v + R)
for q, U in w['start_extra'].items():
    require(int(q) in helpers, 'non-helper entrance')
    cur[int(q)] = span(U)
start = cur.copy()
paid = Counter()


def climb(q, U):
    require(cur[q] & ~U == 0, f'frame not monotone at register {q}')
    if rank(U) > rank(cur[q]):
        paid[rank(U) - rank(cur[q])] += 1
    cur[q] = U


for g in w['A']:
    for q in regs(g):
        climb(q, span(g[-1]))
levels = {int(t): span(U) for t, U in w['target_levels'].items()}
require(all(cur[v + t] == levels.get(t, span([])) for t in range(v)), 'target levels at cut')
for q, U in zip(w['centers'], w['center_frames']):
    U = span(U)
    require(cur[q] == U, 'centre frame')
    for T in sorted({levels.get(g[1] - v, span([])) for g in w['cut'] if g[2] == q}, key=rank, reverse=True):
        require(T & ~U == 0, 'centre path not nested')
        if T != U:
            paid[rank(U) - rank(T)] += 1
        U = T
for g in w['B']:
    for q in regs(g):
        climb(q, span(g[-1]))
endB = cur.copy()
for g in tail:
    for q in regs(g):
        climb(q, span(g[-1]))
end = [full] * v + [span([x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0]) for p in w['ports']] + [full] * R
for q, U in w['helper_final'].items():
    end[int(q)] = span(U)
for q in range(N):
    climb(q, end[q])
require(all(end[q] == full for g in clean for q in regs(g)), 'full cleanup reads a low end')
widths = Counter(rank(end[q]) - rank(start[q]) for q in helpers)

# 4. Low-end cones: rows of prefix^-1 and columns of prefix at each low end stay inside its end frame.
compgates = [['add', int(y), int(k), c.numerator, c.denominator, []] for y, k in pairs for c in [comp.entry(y, k)]]
prefix = w['precondition'] + compgates + main
fwd, inv = nonzero(product(prefix)), nonzero(product(prefix, inverse=True))
for q in lowends:
    require(all(endB[k] & ~end[q] == 0 for k in np.nonzero(inv[q])[0]), f'inverse-row cone {q}')
    require(all(endB[k] & ~end[q] == 0 for k in np.nonzero(fwd[:, q])[0] if k != q), f'dirt-column cone {q}')
print('cones pass for', len(lowends), 'low ends;', len(entering), 'entering;', len(lowends - entering), 'cold ends')
profile = {k: paid[k] for k in sorted(paid)}
print('profile', profile, 'widths', dict(sorted(widths.items())))
if len(sys.argv) > 2:
    want = json.loads(sys.argv[2])
    require(profile == {int(k): x for k, x in want['profile'].items()}, 'profile differs from claim')
    require(dict(widths) == {int(k): x for k, x in want['widths'].items()}, 'widths differ from claim')
print('PASS')
