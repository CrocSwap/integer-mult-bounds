"""P104 t = -1 laws 2 and 3: the carried-row law (one owned MOVE cuts the V-span deficiency by at most 1) and
multi-hub additivity (per-hub deficiencies telescope to dim K). Standard library only, exact rationals.

Law 2 (carried-row). Arrivals A_sigma live over base symbols plus inert symbols sigma_1..sigma_s (one per owned
MOVE); the real word substitutes sigma_m -> c_m. With targets T sigma-free,
D = dim(T + pi A) - dim(pi A) >= D0 - s, D0 = dim(T + A_sigma) - dim(A_sigma). Checked on 3,000 seeded random
worlds (base dim 6..12, s = 0..4, substitutions with base-only and chained contents); the bound is attained
(D = D0 - s) in a positive fraction; control: the strengthened bound D >= D0 - s + 1 is violated.

Law 3 (hub additivity). K = ker G (atom set empty). Hubs j = 1..m finalise the X's in S_j; the witness at hub j is
K_j = {k in K : k_fwd_j = 0} and D_j = rank(K_j restricted to S_j) = dim K_j - dim{k in K_j : k_S_j = 0}.
  nested (fwd_j = S_<j): sum D_j = dim K;   no forwarding: sum D_j >= dim K.
Checked on all 4,683 ordered hub sequences at A3, 4,000 seeded random ones at A4, and on E8/P104 for every
hyperplane hub of the label pairing (510 hubs, then V), 300 non-nested hyperplane pairs, and one hub per port.
Control: the last hub alone (D_V) falls well below dim K. Prints PASS_T1_KERNEL_BILLS."""
import hashlib, itertools, os, random
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def rank(rows):
    piv = {}
    r = 0
    for row in rows:
        v = {k: Fr(x) for k, x in row.items() if x}
        while v:
            k = min(v)
            if k in piv:
                c = v[k]
                for kk, xx in piv[k].items():
                    nv = v.get(kk, 0) - c * xx
                    if nv:
                        v[kk] = nv
                    else:
                        v.pop(kk, None)
            else:
                c = v[k]
                piv[k] = {kk: xx / c for kk, xx in v.items()}
                r += 1
                break
    return r


# ---------------------------------------------------------------------------------------------- law 2
def rand_row(rng, keys, dens):
    return {k: Fr(rng.randint(-3, 3)) for k in keys if rng.random() < dens}


def carried_row():
    say('== law 2: carried-row bound D >= D0 - s')
    rng = random.Random(2026)
    trials = attained = ctl = 0
    for _ in range(3000):
        b = rng.randint(6, 12)
        s = rng.randint(0, 4)
        base = ['b%d' % i for i in range(b)]
        sig = ['s%d' % i for i in range(s)]
        A = [rand_row(rng, base, 0.3) for _ in range(rng.randint(1, b))]
        for _ in range(rng.randint(0, 2 * s + 1)):          # arrivals that carry sigma content
            r = rand_row(rng, base, 0.2)
            for sg in sig:
                if rng.random() < 0.5:
                    r[sg] = Fr(rng.choice([-1, 1, 2]))
            A.append(r)
        T = [rand_row(rng, base, 0.4) for _ in range(rng.randint(1, b // 2 + 1))]
        # substitution sigma_m -> c_m; chained: c_m may itself be a target or an earlier sigma's content
        sub = {}
        for i, sg in enumerate(sig):
            mode = rng.random()
            if mode < 0.4 and T:
                c = dict(rng.choice(T))
            elif mode < 0.6 and i:
                c = dict(sub[sig[rng.randrange(i)]])
                for k, v in rand_row(rng, base, 0.1).items():
                    c[k] = c.get(k, 0) + v
            else:
                c = rand_row(rng, base, 0.3)
            sub[sg] = c

        def pi(r):
            out = {}
            for k, v in r.items():
                for kk, vv in (sub[k].items() if k in sub else [(k, Fr(1))]):
                    out[kk] = out.get(kk, 0) + v * vv
            return {k: v for k, v in out.items() if v}
        D0 = rank(A + T) - rank(A)
        PA = [pi(r) for r in A]
        D = rank(PA + T) - rank(PA)
        if D < D0 - s:
            raise SystemExit('FAIL carried-row law: D=%d D0=%d s=%d' % (D, D0, s))
        trials += 1
        attained += (s > 0 and D == D0 - s)
        ctl += (D < D0 - s + 1)
    expect('random worlds checked', trials, 3000)
    say('ok  bound attained with s > 0 on %d worlds' % attained)
    if attained == 0 or ctl == 0:
        raise SystemExit('FAIL control: bound never tight')
    say('ok  control: D >= D0 - s + 1 is violated on %d worlds' % ctl)


# ---------------------------------------------------------------------------------------------- law 3
class Alg:
    def __init__(self, G):
        self.G = G
        self.n = len(G)
        self.c = {}

    def zdim(self, A):                       # dim{k in ker G : k_A = 0}
        A = frozenset(A)
        if A not in self.c:
            C = [i for i in range(self.n) if i not in A]
            rk = rank([{j: self.G[i][c] for j, c in enumerate(C) if self.G[i][c]} for i in range(self.n)]) if C else 0
            self.c[A] = len(C) - rk
        return self.c[A]

    def Dj(self, S, fwd):
        return self.zdim(fwd) - self.zdim(set(fwd) | set(S))

    def chain(self, seq):
        out, done = [], set()
        for S in seq:
            out.append(self.Dj(S, done))
            done |= set(S)
        return out

    def flat(self, seq):
        out = [self.Dj(S, ()) for S in seq[:-1]]
        prev = set().union(*map(set, seq[:-1])) if len(seq) > 1 else set()
        return out + [self.Dj(seq[-1], prev)]


def ordered_partitions(xs):
    xs = list(xs)
    if not xs:
        yield []
        return
    for k in range(1, len(xs) + 1):
        for first in itertools.combinations(xs, k):
            rest = [x for x in xs if x not in first]
            for p in ordered_partitions(rest):
                yield [first] + p


def toyG(m):
    pairs = list(itertools.combinations(range(m + 1), 2))
    roots = [[(1 if k == i else -1 if k == j else 0) for k in range(m + 1)] for i, j in pairs]
    return [[sum(a * b for a, b in zip(r, s)) for s in roots] for r in roots]


def hubs():
    say('== law 3: hub additivity')
    for m in (3, 4):
        G = toyG(m)
        A = Alg(G)
        n = len(G)
        dK = A.zdim(())
        expect('A%d dim K' % m, dK, n - m)
        if m == 3:
            seqs = list(ordered_partitions(range(n)))
        else:
            rng = random.Random(7)
            seqs = []
            for _ in range(4000):
                k = rng.randint(2, 5)
                lab = [rng.randrange(k) for _ in range(n)]
                seq = [tuple(i for i in range(n) if lab[i] == j) for j in range(k)]
                seqs.append([s for s in seq if s])
        nested = sum(sum(A.chain(s)) == dK for s in seqs)
        fl = [sum(A.flat(s)) for s in seqs]
        expect('A%d nested sum D_j = dim K on all %d sequences' % (m, len(seqs)), nested, len(seqs))
        expect('A%d no-forwarding sum D_j >= dim K' % m, min(fl) >= dK, True)
        say('    A%d no-forwarding sums in [%d, %d]' % (m, min(fl), max(fl)))
    # E8 / P104
    raw = open(os.path.join(ROOT, PR968), 'rb').read()
    expect('SHA256 of %s' % PR968, hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    L = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' t:')]
    n = len(Dr[0])
    G = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(n)] for i in range(n)]
    A = Alg(G)
    dK = A.zdim(())
    expect('E8/P104 dim K', dK, 96)
    # label pairing: S(i,j) = 1 iff <r_i, r_j> even; its F2 row space = the label functionals
    rows = [sum(1 << j for j in range(n) if G[i][j] % 2 == 0) for i in range(n)]
    basis = []
    for r in rows:
        for bb in basis:
            r = min(r, r ^ bb)
        if r:
            basis.append(r)
    expect('F2 rank of the label pairing on the 104 ports', len(basis), 9)
    full = (1 << n) - 1
    hubsets = set()
    for c in range(1, 1 << len(basis)):
        f = 0
        for i, bb in enumerate(basis):
            if c >> i & 1:
                f ^= bb
        zero = full & ~f
        if 0 < bin(zero).count('1') < n:
            hubsets.add(zero)
    H = [[i for i in range(n) if z >> i & 1] for z in sorted(hubsets)]
    expect('hyperplane hubs, sizes', (len(H), sorted({len(S) for S in H})), (510, [44, 48, 52, 56, 60]))
    d1 = [A.Dj(S, ()) for S in H]
    dv = [A.zdim(S) for S in H]
    expect('nested two-hub D1 + D_V = 96 on all hubs', sum(x + y == dK for x, y in zip(d1, dv)), len(H))
    say('ok  D1 in [%d, %d], D_V in [%d, %d]' % (min(d1), max(d1), min(dv), max(dv)))
    if min(dv) >= dK:
        raise SystemExit('FAIL control')
    say('ok  control: counting the last hub alone gives as little as %d < 96' % min(dv))
    rng = random.Random(11)
    ex = []
    for _ in range(300):
        S1, S2 = rng.sample(H, 2)
        S2 = [p for p in S2 if p not in S1]
        rest = [p for p in range(n) if p not in S1 and p not in S2]
        seq = [s for s in (tuple(S1), tuple(S2), tuple(rest)) if s]
        ex.append(sum(A.flat(seq)) - dK)
    expect('non-nested hyperplane pairs + V: excess over 96 >= 0', min(ex) >= 0, True)
    say('    excess in [%d, %d]' % (min(ex), max(ex)))
    seq = [(p,) for p in range(n)]
    expect('one hub per port, nested', sum(A.chain(seq)), 96)
    expect('one hub per port, no forwarding', sum(A.flat(seq)), 103)


if __name__ == '__main__':
    carried_row()
    hubs()
    say('PASS_T1_KERNEL_BILLS')
