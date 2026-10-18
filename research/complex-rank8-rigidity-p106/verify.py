#!/usr/bin/env python3
"""Every P107 unit (P112 minus five lines) and every P106 unit (P112 minus six lines) has a pivot frame that
satisfies PR1560's frame-incidence criterion: (D) diagonal incidence saturation, (G) two-point frame-intersection
connectivity, (W) complete-class-plus-one pair cover, and the nonempty-block premise of its Corollary 2.

Standard library only, exact arithmetic. Self-contained: own E8 model, stabiliser orbits on triples, a three-level
candidate coverage argument (quadruples, 5-subsets, 6-subsets) with explicit generator words (COVER.json.gz),
and per-unit pivot checks (UNITS.json). Both files were produced by make_units.py (numpy); this file rechecks
everything it relies on. Run from the repository root:

    python3 -I -B research/complex-rank8-rigidity-p106/verify.py [--level 5|6] [--part i/n] [--jobs N]

--level 5 checks the coverage words of all three levels and the P107 units; --level 6 checks the P106 units
(with --part i/n, every n-th one starting at the i-th, so the registered replay can split them). With no
--level, both run.
"""

import argparse
import gzip
import itertools
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []
PRIME = 1000003


def check(tag, cond, info=''):
    RESULTS.append(tag)
    print(f"{'PASS' if cond else 'FAIL'} {tag}" + (f': {info}' if info else ''), flush=True)
    if not cond:
        print(f'FAIL_COMPLEX_RANK8_RIGIDITY_P106: {tag}')
        sys.exit(1)


# ---------------------------------------------------------------- E8 model (doubled coordinates, norm 8)

def lines_e8():
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for sj in (2, -2):
            v = [0] * 8
            v[i], v[j] = 2, sj
            out.add(tuple(v))
    for s in itertools.product((1, -1), repeat=7):
        v = (1,) + s
        if v.count(-1) % 2 == 0:
            out.add(v)
    return sorted(out)


# Line IDs are positions in this sorted list; they agree with PR1560's IDs (FRAME0 = 0 1 6 11 20 29 106 119).
LINES = lines_e8()
NL = len(LINES)
IDX = {v: n for n, v in enumerate(LINES)}


def canon(v):
    v = tuple(v)
    first = next(a for a in v if a)
    return v if first > 0 else tuple(-a for a in v)


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]


def lid(v):
    return IDX[canon(v)]


FRAME0 = frozenset(lid(v) for v in [
    (2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0),
    (0, 0, 0, 0, 2, 2, 0, 0), (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 0, 2, 2), (0, 0, 0, 0, 0, 0, 2, -2)])
P112 = [i for i in range(NL) if i not in FRAME0]

# UNITS.json: {"p107": [[5 deleted IDs, 8 pivot IDs], ...], "p106": [[6 deleted IDs, 8 pivot IDs], ...]}.
# COVER.json.gz: "reps4", the 180 quadruple representatives; "cover4", "cover5", "cover6", one [index, word] per
# candidate in the sorted candidate order this file regenerates. A word is a string of generator indices,
# applied left to right, carrying the indexed representative or unit onto the candidate.
UNITS_FILE = HERE / 'UNITS.json'
COVER_FILE = HERE / 'COVER.json.gz'
# Every 29th stabiliser generator (8 of 204), as in the P108 and P107 packages. Orbits under any subgroup of the
# FRAME0 stabiliser are sound for transport (PR1212 section 10).
GEN_STEP = 29


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


def reflection_perm(r):
    rv = LINES[r]
    return tuple(lid(tuple(a - G[i][r] * b for a, b in zip(LINES[i], rv))) for i in range(NL))


def stabiliser(frame):
    refl = [reflection_perm(r) for r in range(NL)]
    gens = [p for p in refl if frozenset(p[i] for i in frame) == frame]
    for p, q in itertools.combinations(refl, 2):
        pq = tuple(p[q[i]] for i in range(NL))
        if frozenset(pq[i] for i in frame) == frame:
            gens.append(pq)
    return gens


def frames_inside(live):
    live = sorted(live)
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(cur)
            return
        for n, j in enumerate(cand):
            grow(cur + [j], [k for k in cand[n + 1:] if G[j][k] == 0])

    grow([], live)
    return out


def triple_orbits(gens):
    """Union-find orbits of the gens on 3-subsets of P112 (as sorted line-id triples)."""
    subs = list(itertools.combinations(P112, 3))
    idx = {s: n for n, s in enumerate(subs)}
    par = list(range(len(subs)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for g in gens:
        for n, s in enumerate(subs):
            a, b = find(n), find(idx[tuple(sorted(g[x] for x in s))])
            if a != b:
                par[a] = b
    orbs = {}
    for n, s in enumerate(subs):
        orbs.setdefault(find(n), []).append(s)
    return sorted(orbs.values(), key=lambda o: (len(o), o[0]))


def apply_word(gens, word, Y):
    for w in word:
        g = gens[int(w)]
        Y = tuple(sorted(g[y] for y in Y))
    return Y


FRAMES = [tuple(F) for F in frames_inside(range(NL))]
FMASK = [sum(1 << i for i in F) for F in FRAMES]
F0MASK = sum(1 << i for i in FRAME0)


# ---------------------------------------------------------------- PR1560's criterion at one pivot

def rank_mod(rows, target):
    """Rank modulo PRIME of 0-1 rows given as tuples of their 1-columns, stopping once it reaches target. A
    nonzero minor modulo a prime is a nonzero integer minor, so this is a lower bound on the rank over Q."""
    basis = {}
    for cols in rows:
        v = dict.fromkeys(cols, 1)
        while v:
            c = min(v)
            w = basis.get(c)
            if w is None:
                inv = pow(v[c], -1, PRIME)
                basis[c] = {d: x * inv % PRIME for d, x in v.items()}
                break
            a = v[c]
            for d, x in w.items():
                y = (v.get(d, 0) - a * x) % PRIME
                if y:
                    v[d] = y
                else:
                    del v[d]
        if len(basis) >= target:
            break
    return len(basis)


def rank_dense(rows):
    """Rank modulo PRIME of small integer rows (a lower bound on the rank over Q)."""
    basis = {}
    for row in rows:
        v = [x % PRIME for x in row]
        for j in sorted(basis):
            if v[j]:
                a, w = v[j], basis[j]
                v = [(x - a * y) % PRIME for x, y in zip(v, w)]
        j = next((j for j, x in enumerate(v) if x), None)
        if j is not None:
            inv = pow(v[j], -1, PRIME)
            basis[j] = [x * inv % PRIME for x in v]
    return len(basis)


def criterion(X, F, frames=None, skip_g=False):
    """(None, stats) if pivot F satisfies (D), (G), (W) and nonempty blocks on the live set P112 \\ X, using
    the family of all live frames; else (reason, None). frames (a sub-family) and skip_g serve the negative
    controls only."""
    xm = F0MASK | sum(1 << i for i in X)
    fm = sum(1 << i for i in F)
    if fm & xm or not is_frame(F):
        return 'pivot', None
    live_frames = [m for m in FMASK if not m & xm]
    if frames is not None:
        if not set(frames) <= set(live_frames):
            return 'frames', None
        live_frames = frames
    non = [i for i in P112 if not (xm | fm) >> i & 1]
    # Blocks relative to F: T_i = pivot coordinates odd to i; class = parity of the negative signs on T_i.
    blocks = {}
    for i in non:
        t = tuple(n for n in range(8) if G[i][F[n]])
        if len(t) != 4:
            return 'support', None
        blocks.setdefault(t, [0, 0])[sum(G[i][F[n]] < 0 for n in t) % 2] += 1
    if len(blocks) != 14:
        return 'nonempty-blocks', None
    # (W): every pivot pair lies in a block with one complete live class (4 lines) and a live line of the other.
    cov = set()
    for t, (c0, c1) in blocks.items():
        if (c0 == 4 and c1) or (c1 == 4 and c0):
            cov.update(itertools.combinations(t, 2))
    if len(cov) != 28:
        return 'W', None
    # (G): for each pivot pair, the graph on I_kl joining i, j when a live frame meets I_kl in exactly {i, j}.
    for k, l in itertools.combinations(range(8), 2) if not skip_g else ():
        I = [i for i in non if G[i][F[k]] and G[i][F[l]]]
        im = sum(1 << i for i in I)
        adj = {i: set() for i in I}
        for m in live_frames:
            s = m & im
            if s.bit_count() == 2:
                a = s.bit_length() - 1
                b = (s ^ (1 << a)).bit_length() - 1
                adj[a].add(b)
                adj[b].add(a)
        seen, todo = {I[0]}, [I[0]]
        while todo:
            for j in adj[todo.pop()] - seen:
                seen.add(j)
                todo.append(j)
        if len(seen) != len(I):
            return 'G', None
    # (D): for each k, the seven vectors h_kl(i) = G_ik G_il on I_k are independent, and the incidence matrix
    # of live frames against I_k has rank |I_k| - 7. The h_kl lie in its kernel by identity (6), checked
    # globally in main() for every frame, so the kernel is exactly their span.
    ranks = []
    for k in range(8):
        I = [i for i in non if G[i][F[k]]]
        pos = {i: n for n, i in enumerate(I)}
        h = [[G[i][F[k]] * G[i][F[l]] for l in range(8) if l != k] for i in I]
        if rank_dense(h) != 7:
            return 'D-kernel-vectors', None
        rows = sorted({tuple(pos[i] for i in I if m >> i & 1) for m in live_frames} - {()})
        if rank_mod(rows, len(I) - 7) != len(I) - 7:
            return 'D', None
        ranks.append(len(I) - 7)
    full = sum(1 for c in blocks.values() if c == [4, 4])
    return None, (len(live_frames), min(ranks), max(ranks), full)


def check_unit(u):
    X, F = tuple(u[:-8]), tuple(u[-8:])
    return criterion(X, F)


def check_units(units, size, jobs):
    bad, stats = [], []
    ok_shape = all(len(u) == size + 8 and len(set(u[:size])) == size and set(u[:size]) <= set(P112)
                   for u in units)
    with ProcessPoolExecutor(jobs) as ex:
        for n, (reason, st) in enumerate(ex.map(check_unit, units, chunksize=64)):
            if reason is not None:
                bad.append((n, reason))
            else:
                stats.append(st)
    return ok_shape and not bad, bad, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', type=int, choices=(5, 6))
    ap.add_argument('--part', default='1/1', help='i/n: check every n-th P106 unit starting at the i-th')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()
    part, nparts = map(int, args.part.split('/'))
    levels = (5, 6) if args.level is None else (args.level,)
    check('model.lines', NL == 120 and len(FRAME0) == 8 and is_frame(sorted(FRAME0))
          and sorted(FRAME0) == [0, 1, 6, 11, 20, 29, 106, 119], '120 lines; FRAME0 is a frame, IDs as in PR1560')
    # Identity (6) of PR1560 for every frame S: sum over S of v v^T is 8 I, so sum_{i in S} G_ik G_il = 2 G_kl
    # for all lines k, l. This puts the h_kl in the kernel of every incidence matrix used in (D) and gives the
    # opposite signs on the edges of the (G) graphs.
    check('model.frame-identity', len(FRAMES) == 2025 and all(
        all(sum(LINES[i][a] * LINES[i][b] for i in S) == (8 if a == b else 0) for a in range(8) for b in range(8))
        for S in FRAMES), '2025 frames; each satisfies sum over the frame of v v^T = 8 I (identity (6))')
    UNITS = json.loads(UNITS_FILE.read_text())
    u5 = [tuple(u[:5]) for u in UNITS['p107']]
    if 5 in levels:
        allgens = stabiliser(FRAME0)
        gens = allgens[::GEN_STEP]
        check('model.generators', len(allgens) == 204 and all(frozenset(g[i] for i in FRAME0) == FRAME0
                                                               for g in gens),
              f'{len(gens)} of the {len(allgens)} reflection / reflection-pair generators fixing FRAME0')
        torbs = triple_orbits(gens)
        check('census.triples', len(torbs) == 24 and sum(map(len, torbs)) == 227920,
              'the generators split the 227920 triples of P112 into 24 orbits')
        cover = json.loads(gzip.decompress(COVER_FILE.read_bytes()))
        reps4 = [tuple(r) for r in cover['reps4']]
        # Level 1. Every quadruple Y contains a triple s = h(t) with t a triple-orbit representative, so h^-1(Y)
        # is a candidate t + {x}; each candidate is a word applied to a quadruple representative.
        c4 = sorted({tuple(sorted(o[0] + (x,))) for o in torbs for x in P112 if x not in o[0]})
        ok = len(cover['cover4']) == len(c4) and all(len(set(r)) == 4 and set(r) <= set(P112) for r in reps4)
        ok &= all(apply_word(gens, w, reps4[j]) == c for c, (j, w) in zip(c4, cover['cover4']))
        check('census.cover4', ok, f'{len(c4)} quadruple candidates, each a generator word applied to one of '
              f'{len(reps4)} quadruple representatives: every quadruple of P112 is equivalent to one of them')
        # Level 2. Every 5-subset contains a quadruple equivalent to a representative r, so it is equivalent to
        # a candidate r + {x}; each candidate is a word applied to a P107 unit.
        c5 = sorted({tuple(sorted(r + (x,))) for r in reps4 for x in P112 if x not in r})
        ok = len(cover['cover5']) == len(c5)
        ok &= all(apply_word(gens, w, u5[j]) == c for c, (j, w) in zip(c5, cover['cover5']))
        hit = {j for j, _ in cover['cover5']}
        check('census.cover5', ok and hit == set(range(len(u5))),
              f'{len(c5)} 5-subset candidates (quadruple representative + one line), each a generator word '
              f'applied to one of the {len(u5)} P107 units: every 5-subset of P112 is equivalent to a unit')
        # Level 3. Likewise every 6-subset is equivalent to a P107 unit plus one line.
        u6 = [tuple(u[:6]) for u in UNITS['p106']]
        c6 = sorted({tuple(sorted(r + (x,))) for r in u5 for x in P112 if x not in r})
        ok = len(cover['cover6']) == len(c6)
        ok &= all(apply_word(gens, w, u6[j]) == c for c, (j, w) in zip(c6, cover['cover6']))
        hit = {j for j, _ in cover['cover6']}
        check('census.cover6', ok and hit == set(range(len(u6))),
              f'{len(c6)} 6-subset candidates (P107 unit + one line), each a generator word applied to one of '
              f'the {len(u6)} P106 units: every 6-subset of P112 is equivalent to a unit; max word length '
              f'{max(len(w) for _, w in cover["cover6"])}')
        # Controls. PR1560's coverage-failure control fails (W) at its pivot but passes at another; and the
        # pivot rule is not vacuous on the units.
        Xc = (3, 13, 14, 22, 23)
        r1, _ = criterion(Xc, (2, 5, 8, 9, 30, 41, 108, 117))
        r2, _ = criterion(Xc, (2, 5, 15, 16, 30, 41, 109, 116))
        r3, _ = criterion((32, 45, 73, 78, 88), (2, 5, 8, 9, 30, 41, 108, 117))
        check('control.pr1560', r1 == 'W' and r2 is None and r3 is None,
              "PR1560's fixture passes; its control (3,13,14,22,23) fails (W) at PR1560's pivot and passes at "
              "(2,5,15,16,30,41,109,116)")
        # (G) and (D) are not vacuous: on PR1560's fixture, the pivot alone (PR1560's own control) and the first
        # 250 live frames are frame families on which (G) fails and, checked by itself, so does (D).
        Xf, Ff = (32, 45, 73, 78, 88), (2, 5, 8, 9, 30, 41, 108, 117)
        xm = F0MASK | sum(1 << i for i in Xf)
        fams = [[sum(1 << i for i in Ff)], [m for m in FMASK if not m & xm][:250]]
        check('control.rank-and-graph', all(criterion(Xf, Ff, f)[0] == 'G' and criterion(Xf, Ff, f, True)[0] == 'D'
                                            for f in fams),
              "on PR1560's fixture, the pivot alone and the first 250 live frames each fail (G), and (D) by itself")
        fails = {}
        for u in UNITS['p107']:
            xm = F0MASK | sum(1 << i for i in u[:5])
            first = next(F for F, m in zip(FRAMES, FMASK) if not m & xm)
            r = criterion(u[:5], first)[0]
            fails[r] = fails.get(r, 0) + 1
        check('control.first-frame', sum(v for k, v in fails.items() if k is not None) > 0,
              'first live frame per P107 unit: ' + ', '.join(f'{k or "passes"} {v}' for k, v in
                                                             sorted(fails.items(), key=lambda kv: str(kv[0]))))
        ok, bad, st = check_units(UNITS['p107'], 5, args.jobs)
        check('units.p107', ok and len(u5) == 1614,
              f'{len(u5)} P107 units: the pivot is a live frame and passes (D), (G), (W) and nonempty blocks; '
              f'{min(s[0] for s in st)}-{max(s[0] for s in st)} live frames, (D) ranks {min(s[1] for s in st)}-'
              f'{max(s[2] for s in st)}, {min(s[3] for s in st)}-{max(s[3] for s in st)} fully live blocks, '
              f'{len({tuple(u[5:]) for u in UNITS["p107"]})} distinct pivots' + (f'; failing {bad[:5]}' if bad else ''))
    if 6 in levels:
        mine = UNITS['p106'][part - 1::nparts]
        ok, bad, st = check_units(mine, 6, args.jobs)
        check('units.p106', ok and len(UNITS['p106']) == 19295 and 1 <= part <= nparts,
              f'part {part}/{nparts}: {len(mine)} of the {len(UNITS["p106"])} P106 units: the pivot is a live '
              f'frame and passes (D), (G), (W) and nonempty blocks; {min(s[0] for s in st)}-{max(s[0] for s in st)} live frames, (D) ranks '
              f'{min(s[1] for s in st)}-{max(s[2] for s in st)}, {min(s[3] for s in st)}-{max(s[3] for s in st)} '
              f'fully live blocks, {len({tuple(u[6:]) for u in mine})} distinct pivots'
              + (f'; failing {bad[:5]}' if bad else ''))
    print(f'PASS_COMPLEX_RANK8_RIGIDITY_P106: checks {len(RESULTS)}; levels {"+".join(map(str, levels))}'
          + (f' (P106 part {part}/{nparts})' if 6 in levels else '') + ': '
          + ('every 5-subset and 6-subset of P112 is equivalent to a unit; ' if 5 in levels else '')
          + 'every unit has a pivot satisfying PR1560 (D), (G), (W) and nonempty blocks')


if __name__ == '__main__':
    main()
