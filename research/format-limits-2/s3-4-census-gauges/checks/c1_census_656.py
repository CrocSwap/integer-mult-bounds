"""C1: provenance census of the shipped #656 gauge44 word (492 helpers, 4 allocation sites) and the exact kappa identity.
Inputs: PR 656 data/PLAN.json (blob-checked), the rebuilt canonical word (hash-pinned by that PLAN), TAGS.json (rebuilt annotation, NOT pinned)."""
import math
from collections import Counter, defaultdict
from decimal import Decimal as D, localcontext
from common import *

plan = load_json('pr656', 'PLAN.json.gz'); d = load_json('derived', 'g44-CANONICAL-WORD.json.gz')
M, W, deficit = plan['M'], plan['live'], plan['deficit']
H = {int(k): v for k, v in plan['profile'].items()}

def root(H):
    with localcontext() as c:
        c.prec = 50
        terms = [(D(r) * D(n) / D(M * W), (D(M) / D(r)).ln()) for r, n in H.items() if n]
        lo, hi = D(0), D('0.01')
        for _ in range(300):
            a = (lo + hi) / 2
            if sum(p * (a * l).exp() for p, l in terms) < 1: lo = a
            else: hi = a
        return (lo + hi) / 2

# ---- kappa identity (needs only the PR file)
check('C1 PLAN mass = M*W - deficit', sum(r * n for r, n in H.items()) == M * W - deficit, '%d = 73*7168-2560' % (M * W - deficit))
b = root(H); kappa = b / (1 + b)
check('C1 root(PLAN profile): b = 0.00165684913780230798', str(b).startswith('0.00165684913780230798'), str(b)[:26])
check('C1 kappa = b/(1+b) = 1.654108529511355e-3', str(kappa).startswith('0.001654108529511355'), str(kappa)[:24])

# ---- per-register climbs of the word (port of the replay used by the cards; climb = frame-dimension increase on first use or at the end)
def climbs(d):
    F = {(p, i): e[-1] for p in ('A', 'B', 'tail') for i, e in enumerate(d[p])}
    fr = d['frames']; cur = list(d['start']); out = []
    L = lambda f: len(fr[f])
    def climb(r, f):
        if cur[r] == f: return
        out.append((r, L(f) - L(cur[r]))); cur[r] = f
    for part in ('A', 'centers', 'B', 'tail', 'final'):
        if part in ('A', 'B', 'tail'):
            for i, e in enumerate(d[part]):
                for r in [e[1]] + ([e[2]] if e[0] == 'add' else []): climb(r, F[part, i])
        elif part == 'centers':
            for k, r in enumerate(d['centers']):
                cf = d['center_frames'][k]
                terms = [e for e in d['cut'] if e[2] == r]
                path = [cf] + sorted({0 for e in terms} - {cf}, key=lambda x: -L(x))
                for a in range(1, len(path)): out.append((r, L(path[a - 1]) - L(path[a])))
        else:
            for r, f in enumerate(d['final']): climb(r, f)
    return out
out = climbs(d); v, R = d['v'], d['R']
prof = Counter(w for r, w in out)
lp = {int(k): n for k, n in d['local_profile'].items()}
check('C1 word local_profile {1:2542,2:414,3:434,4:154,5:56,8:8}', lp == {1: 2542, 2: 414, 3: 434, 4: 154, 5: 56, 8: 8}, lp)
check('C1 replayed climb profile == local_profile (3608 climbs)', dict(prof) == lp and sum(prof.values()) == 3608, sum(prof.values()))
ex = Counter(H)
for r, n in lp.items(): ex[r] -= 72 * n
ex = {r: n for r, n in ex.items() if n}
check('C1 PLAN profile = 72 x local profile + non-register extras {2:4,3:4,5:1,7:1,16:2,32:1,48:2398}', ex == {2: 4, 3: 4, 5: 1, 7: 1, 16: 2, 32: 1, 48: 2398}, ex)

# ---- allocation sites (TAGS.json: rebuilt annotation, not pinned by the PR)
T = load_json('derived', 'g44-TAGS.json'); tag = {int(k) - 16: x for k, x in T.items()}
check('C1 TAGS cover exactly the 492 helper ids', R == 492 and set(tag) == set(range(2 * v, 2 * v + R)) and v == 112, (v, R))
cen = set(d['centers']); phi = lambda r: r * math.log(73 / r)
per = defaultdict(list)
for r, w in out: per[r].append(w)
site = {r: tag[r][0][0] for r in tag}
cnt = Counter(site.values())
check('C1 helpers born at 4 sites: S1 block scratch 224, S3 packet copy 156, S4 slot copy 112 (sum 492)',
      len(cnt) == 3 and sum(cnt.values()) == 492 and sorted(cnt.values()) == [112, 156, 224], dict(cnt))
s1c = sorted(r for r in cen if r in tag)
check('C1 S1 = 221 + 3 centres (the 3 centres among helper ids are S1 slots 224, 240, 256)', s1c == [224, 240, 256] and all(site[r].startswith('S1') for r in s1c) and sum(1 for r in tag if site[r].startswith('S1') and r not in cen) == 221, s1c)
mass = {s: sum(phi(w) for r in tag if site[r] == s for w in per[r]) for s in cnt}
S1, S3, S4 = [next(s for s in cnt if s.startswith(p)) for p in ('S1', 'S3', 'S4')]
hel = sum(mass.values()); xy = sum(phi(w) for r, w in out if r < 2 * v)
glob = sum(phi(r) * n for r, n in H.items()) / 72
check('C1 narrow mass per call (sum r ln(73/r) over climbs): S1 6902, S3 4430, S4 2754', all(abs(mass[s] - x) < 0.6 for s, x in zip((S1, S3, S4), (6902, 4430, 2754))), [round(mass[s], 1) for s in (S1, S3, S4)])
check('C1 helpers 14085, X/Y registers 6637; helpers = 68% of register narrow mass', round(hel) == 14085 and round(xy) == 6637 and round(100 * hel / (hel + xy)) == 68, (round(hel), round(xy)))
check('C1 share of global narrow mass 32.3 / 20.7 / 12.9 % (global incl. 3.1% idle windows, 31.0% X/Y)', [round(100 * mass[s] / glob, 1) for s in (S1, S3, S4)] == [32.3, 20.7, 12.9] and round(100 * xy / glob, 1) == 31.0 and round(100 * (glob - hel - xy) / glob, 1) == 3.1, round(glob))
sh = [100 * mass[s] / hel for s in (S1, S3, S4)]
c3 = sum(phi(w) for r in tag if r in cen for w in per[r])
check('C1 share of helper narrow mass (S1 without centres) 47.9 / 31.4 / 19.5 %', [round(100 * (mass[S1] - c3) / hel, 1), round(sh[1], 1), round(sh[2], 1)] == [47.9, 31.4, 19.5], [round(100 * (mass[S1] - c3) / hel, 1), round(sh[1], 1), round(sh[2], 1)])
check('C1 S3 + S4 = 268 helpers (numerical equality with the pure-dirt count of C2)', cnt[S3] + cnt[S4] == 268)
finish()
