#!/usr/bin/env python3
"""Independent two-stage check of the deferred complex word (Swapnil Jain's deferred readouts on the complex
network, PR #110's construction) from its exported schedule. Own event expansion and value replay; the F2 algebra
is scripts/deferred_product/complex_frames.py.

Values (mod p = 2^61 - 1, random data x, arbitrary scratch):
  V1  every add/copy result equals its DAG node, every root role ends at its root node, and the root nodes are
      the A, D and P roots of the shipped DAG (pinned by sha256);
  V2  phase one is closed under the per-role order of the op list and touches no deferred slot;
  V3  readout functionals are compiled here by reverse propagation (outputs: D roots +1/2, pair-star roots -1/2;
      centre i into target t: 1/21 - [i in t]/2, read from its copy after phase one); their supports equal the
      exported garbage reach;
  V4  the stage-one word runs with arbitrary scratch (readouts of non-deferred slots, early V, phase one, centre
      copies, deferred readouts, deferred V, remaining ops, outputs, inverse ops, -V): every role is restored and
      every y_t gains exactly x_t.
Frames, per invocation (F2-subspaces of F2^h with the dot product; data roles X_t, Y_t):
   1 readouts of non-deferred slots at 0 (slot and every reached target)
   2 early V: non-deferred leaf slots and X_t at <t>
   3 phase-one ops at their node frames
   4 centre copies: copy at the centre's frame, scattered into every target at 0
   5 deferred readouts: slot and reached targets at sigma_u (the placed frame)
   6 deferred V
   7 remaining ops at their node frames
   8 outputs: slot and target at t^perp
   9 every op again at F, in reverse order
  10 -V at F
Every move must be nested with a nondegenerate residual. Alternating residuals are allowed (one child under the
normal form of notes/endpoint-gauge-complex.tex) and counted. Stage two is the same event list reversed, with
complemented frames and the data banks exchanged; it is expanded explicitly, checked the same way, and must return
to the complemented start. A reflected centre copy is created at S^perp and moved up to F (residual S).
Paid histogram: both stages' moves x v, exteriors [m - r_u] x 2v (r_u = h - dim sigma_u), connectors [(h-1)^2]
x 2N, copy corrections [1] x N. It must equal the exported rows and, with --profile, the certified profile; its
rank mass is W m - N + L.
--controls reruns the frame check on five corrupted schedules, each of which must be rejected.
Usage: deferred_word.py WORD.json[.gz] DAG.json.gz [--profile PROFILE.json] [--controls]
"""
import gzip, hashlib, json, random, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deferred_product import complex_frames as cf

make_basis, contains, perp_within, nondegenerate, vecs = cf.make_basis, cf.contains, cf.perp_within, \
    cf.nondegenerate, cf.vecs
P = (1 << 61) - 1


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


# ---------------------------------------------------------------- values
def values(d, dag_path):
    dag_raw = Path(dag_path).read_bytes()
    require(hashlib.sha256(dag_raw).hexdigest() == d['dag_sha256'], 'DAG sha256')
    g = json.loads(gzip.decompress(dag_raw))
    h, v, R = d['h'], d['v'], d['R']
    require((g['h'], g['v']) == (h, v), 'DAG shape')
    args = g['args']
    trip = list(combinations(range(h), 3))
    roots = d['roots']
    require(sorted(r['node'] for r in roots) == sorted(g['A'] + g['D'] + g['P']), 'root nodes')
    require([r['j'] for r in roots] == list(range(len(roots))), 'root order')
    for r in roots:
        if r['kind'] == 'output':
            require(r['target_triple'] == list(trip[r['target']]), 'target triple %d' % r['j'])
        else:
            require(r['kind'] == 'centre' and 0 <= r['centre'] < h, 'centre root %d' % r['j'])
    role_root = {int(s): j for s, j in d['role_root'].items()}
    require(sorted(role_root.values()) == list(range(len(roots))), 'one role per root')
    leaf_of = {int(s): x for s, x in d['leaf_of'].items()}
    ops = d['ops']
    require(all(o[0] in ('add', 'copy', 'src') for o in ops), 'op kinds')
    require({o[1]: o[2] for o in ops if o[0] == 'src'} == leaf_of, 'sources')
    ops = [o for o in ops if o[0] != 'src']
    rng = random.Random(20261009)
    x = [rng.randrange(P) for _ in range(v)]

    # V1: zero-scratch replay against the DAG
    val = [0] * (1 + v + len(args) // 2)
    for i in range(v):
        val[i + 1] = x[i]
    for k in range(len(args) // 2):
        val[v + 1 + k] = (val[args[2 * k]] + val[args[2 * k + 1]]) % P
    a = [0] * R
    for s, leaf in leaf_of.items():
        a[s] = x[leaf - 1]
    for o in ops:
        if o[0] == 'add':
            a[o[1]] = (a[o[1]] + a[o[2]]) % P
            require(a[o[1]] == val[o[3]], 'add result')
        else:
            a[o[2]] = (a[o[2]] + a[o[1]]) % P
            require(a[o[1]] == a[o[2]] == val[o[3]], 'copy result')
    require(all(a[s] == val[roots[j]['node']] for s, j in role_root.items()), 'root values')

    # V2: phase one closed under the per-role order, disjoint from deferred slots
    phase1 = set(d['phase1'])
    deferred = set(d['deferred'])
    off = len(d['ops']) - len(ops)                 # src entries come first
    require(all(o[0] == 'src' for o in d['ops'][:off]), 'src entries first')
    last = {}
    for i, o in enumerate(ops):
        for s in (o[1], o[2]):
            if s in last and i + off in phase1:
                require(last[s] + off in phase1, 'phase one not closed at op %d' % (i + off))
            last[s] = i
    require(all(o[1] not in deferred and o[2] not in deferred for i, o in enumerate(ops) if i + off in phase1),
            'phase one touches a deferred slot')
    early = [o for i, o in enumerate(ops) if i + off in phase1]
    late = [o for i, o in enumerate(ops) if i + off not in phase1]

    # V3: readout functionals; a functional is (sparse {target: coefficient}, {centre: multiplicity})
    half = pow(2, P - 2, P)
    sp = [dict() for _ in range(R)]
    mu = [dict() for _ in range(R)]
    centre_role = {}
    for s, j in role_root.items():
        r = roots[j]
        if r['kind'] == 'output':
            sp[s][r['target']] = half if j < v else P - half
        else:
            centre_role[r['centre']] = s

    def back(seq):
        for o in reversed(seq):
            dst, src = (o[1], o[2]) if o[0] == 'add' else (o[2], o[1])
            ds, ss = sp[dst], sp[src]
            for t, c in ds.items():
                ss[t] = (ss.get(t, 0) + c) % P
            dm, sm = mu[dst], mu[src]
            for i, c in dm.items():
                sm[i] = sm.get(i, 0) + c
    back(late)
    late_sp = {u: dict(sp[u]) for u in deferred}
    require(all(not mu[u] for u in deferred), 'deferred slot reaches a centre')
    for i, s in centre_role.items():
        mu[s][i] = mu[s].get(i, 0) + 1
    back(early)
    reach_all = set(d['reach_all'])
    for u in range(R):
        require(set(sp[u]) == set(d['reach'][str(u)]), 'reach of slot %d' % u)
        require(bool(mu[u]) == (u in reach_all), 'centre reach of slot %d' % u)

    # V4: the stage-one word with arbitrary scratch
    inv21 = pow(21, P - 2, P)
    coef = [[(inv21 - (half if i in T else 0)) % P for T in trip] for i in range(h)]
    gbg = [rng.randrange(P) for _ in range(R)]
    y0 = [rng.randrange(P) for _ in range(v)]
    a, y = list(gbg), list(y0)
    M = [0] * h

    def run(seq, sign=1):
        for o in seq:
            if o[0] == 'add':
                a[o[1]] = (a[o[1]] + sign * a[o[2]]) % P
            else:
                a[o[2]] = (a[o[2]] + sign * a[o[1]]) % P
    for u in range(R):                             # 1
        if u not in deferred:
            for t, c in sp[u].items():
                y[t] = (y[t] - c * a[u]) % P
            for i, c in mu[u].items():
                M[i] = (M[i] + c * a[u]) % P
    for s, leaf in leaf_of.items():                # 2
        if s not in deferred:
            a[s] = (a[s] + x[leaf - 1]) % P
    run(early)                                     # 3
    for i, s in centre_role.items():               # 4: copy, scatter; centre parts of the readouts in 1
        net = (a[s] - M[i]) % P
        for t in range(v):
            y[t] = (y[t] + coef[i][t] * net) % P
    for u in d['deferred']:                        # 5: reads the slot's current content
        for t, c in late_sp[u].items():
            y[t] = (y[t] - c * a[u]) % P
    for s, leaf in leaf_of.items():                # 6
        if s in deferred:
            a[s] = (a[s] + x[leaf - 1]) % P
    run(late)                                      # 7
    for s, j in role_root.items():                 # 8
        r = roots[j]
        if r['kind'] == 'output':
            y[r['target']] = (y[r['target']] + (half if j < v else P - half) * a[s]) % P
    run(reversed(early + late), -1)                # 9
    for s, leaf in leaf_of.items():                # 10
        a[s] = (a[s] - x[leaf - 1]) % P
    require(a == gbg, 'scratch not restored')
    require(all(y[t] == (y0[t] + x[t]) % P for t in range(v)), 'y_t != y0_t + x_t')
    return dict(ops=len(ops), phase_one=len(early), deferred=len(deferred), centres=len(centre_role))


# ---------------------------------------------------------------- frames
def mutate(d, name):
    d = dict(d)
    h, v = d['h'], d['v']
    if name == 'phase1-op':                        # an op on a deferred slot before its deferred readout
        ds, p1 = set(d['deferred']), set(d['phase1'])
        i = next(i for i, o in enumerate(d['ops']) if i not in p1 and o[0] != 'src' and (o[1] in ds or o[2] in ds))
        d['phase1'] = sorted(p1 | {i})
    elif name == 'sigma-full':                     # one deferred slot placed at F
        d['placed'] = dict(d['placed'])
        d['placed'][str(d['deferred'][0])] = [1 << i for i in range(h)]
    elif name == 'frame':                          # the frame of the first later op's node perturbed
        p1 = set(d['phase1'])
        node = next(o[3] for i, o in enumerate(d['ops']) if i not in p1 and o[0] != 'src')
        d['U'] = dict(d['U'])
        d['U'][str(node)] = [d['U'][str(node)][0] ^ 1 << (h - 1)] + d['U'][str(node)][1:]
    elif name == 'drop-copy':                      # one centre read out without its copy
        d['centre_roles'] = d['centre_roles'][1:]
    elif name == 'root':                           # one output read into the wrong target
        d['roots'] = list(d['roots'])
        k = next(k for k, r in enumerate(d['roots']) if r['kind'] == 'output')
        d['roots'][k] = dict(d['roots'][k], target=(d['roots'][k]['target'] + 1) % v)
    else:
        raise SystemExit('unknown mutation ' + name)
    return d


def frames(d):
    h, v, R = d['h'], d['v'], d['R']
    FULL = make_basis([1 << i for i in range(h)])
    ZERO = make_basis([])
    tmask = [sum(1 << p for p in T) for T in combinations(range(h), 3)]
    line = [make_basis([x]) for x in tmask]
    U = {int(n): make_basis(B) for n, B in d['U'].items()}
    sigma = {int(s): make_basis(B) for s, B in d['placed'].items()}
    deferred = list(d['deferred'])
    dset = set(deferred)
    ops = [o for o in d['ops'] if o[0] != 'src']
    off = len(d['ops']) - len(ops)
    phase1 = set(d['phase1'])
    leaf_of = {int(s): x for s, x in d['leaf_of'].items()}
    role_root = {int(s): j for s, j in d['role_root'].items()}
    roots = {r['j']: r for r in d['roots']}
    reach = {int(s): ts for s, ts in d['reach'].items()}
    reach_all = set(d['reach_all'])
    comp_cache = {}

    def comp(B):
        if B not in comp_cache:
            comp_cache[B] = perp_within(FULL, B)
        return comp_cache[B]
    events = []                                    # (frame, roles, kind)

    def targets(s):
        return range(v) if s in reach_all else reach.get(s, [])
    for s in range(R):                             # 1
        if s not in dset:
            events.append((ZERO, (('A', s),) + tuple(('Y', t) for t in targets(s)), 'readout'))
    for s, x in sorted(leaf_of.items()):           # 2
        if s not in dset:
            events.append((line[x - 1], (('A', s), ('X', x - 1)), 'V'))
    for i, o in enumerate(ops):                    # 3
        if i + off in phase1:
            events.append((U[o[3]], (('A', o[1]), ('A', o[2])), o[0]))
    for s in d['centre_roles']:                    # 4
        events.append((None, (('A', s),), 'centre-copy'))
        events.append((ZERO, (('C', s),) + tuple(('Y', t) for t in range(v)), 'centre-scatter'))
    for s in deferred:                             # 5
        events.append((sigma[s], (('A', s),) + tuple(('Y', t) for t in targets(s)), 'deferred-readout'))
    for s in deferred:                             # 6
        if s in leaf_of:
            events.append((line[leaf_of[s] - 1], (('A', s), ('X', leaf_of[s] - 1)), 'deferred-V'))
    for i, o in enumerate(ops):                    # 7
        if i + off not in phase1:
            events.append((U[o[3]], (('A', o[1]), ('A', o[2])), o[0]))
    for s, j in sorted(role_root.items()):         # 8
        if roots[j]['kind'] == 'output':
            t = roots[j]['target']
            events.append((comp(line[t]), (('A', s), ('Y', t)), 'output'))
    for o in reversed(ops):                        # 9
        events.append((FULL, (('A', o[1]), ('A', o[2])), 'inverse-' + o[0]))
    for s, x in sorted(leaf_of.items()):           # 10
        events.append((FULL, (('A', s), ('X', x - 1)), '-V'))

    cache = {}

    def replay(evts, start, label):
        cur = dict(start)
        bad, edges, alternating = [], Counter(), Counter()
        for frame, roles, kind in evts:
            if kind == 'centre-copy':
                (_, s), = roles
                cur[('C', s)] = cur[('A', s)]
                continue
            for r in roles:
                old = cur[r]
                if old == frame:
                    continue
                if r[0] == 'C':
                    # stage one: created at the centre's frame S, moved down to 0 (residual S);
                    # stage two: created at S^perp, moved up to F (residual (S^perp)^perp = S)
                    lo, hi = (frame, old) if len(frame) <= len(old) else (old, frame)
                else:
                    lo, hi = old, frame
                key = (lo, hi)
                if key not in cache:
                    ok = contains(hi, lo)
                    res = (perp_within(hi, lo) if lo else hi) if ok else None
                    cache[key] = (ok and nondegenerate(res),
                                  ok and not any(bin(w).count('1') & 1 for w in vecs(res)))
                ok, alt = cache[key]
                if not ok:
                    bad.append((label, kind, r, len(old), len(frame)))
                if alt:
                    alternating[len(hi) - len(lo)] += 1
                edges[len(hi) - len(lo)] += 1
                cur[r] = frame
        return cur, bad, edges, alternating

    start1 = {('A', s): (sigma[s] if s in dset else ZERO) for s in range(R)}
    start1.update({('X', t): line[t] for t in range(v)})
    start1.update({('Y', t): ZERO for t in range(v)})
    end1, bad1, edges1, alt1 = replay(events, start1, 'stage one')
    ends_ok = all(end1[('A', s)] == FULL for s in range(R)) and all(end1[('X', t)] == FULL for t in range(v)) \
        and all(end1[('Y', t)] == comp(line[t]) for t in range(v))

    swap = lambda r: ('Y', r[1]) if r[0] == 'X' else ('X', r[1]) if r[0] == 'Y' else r
    events2, src = [], {}
    probe = dict(start1)
    for frame, roles, kind in events:              # the frame each centre has when it is copied
        if kind == 'centre-copy':
            src[roles[0][1]] = probe[roles[0]]
        else:
            for r in roles:
                probe[r] = frame
    for frame, roles, kind in reversed(events):
        if kind != 'centre-copy':
            events2.append((comp(frame), tuple(swap(r) for r in roles), kind))
    start2 = {swap(r): comp(f) for r, f in end1.items() if r[0] != 'C'}
    start2.update({('C', s): comp(f) for s, f in src.items()})
    end2, bad2, edges2, alt2 = replay(events2, start2, 'stage two')
    cont_ok = all(end2[swap(r)] == comp(f) for r, f in start1.items())

    m, N = h * h, v * v
    paid = Counter({r: v * n for r, n in edges1.items()})
    paid.update({r: v * n for r, n in edges2.items()})
    for s in range(R):
        paid[m - (h - (len(sigma[s]) if s in dset else 0))] += 2 * v
    paid[(h - 1) ** 2] += 2 * N
    paid[1] += N
    return dict(events=len(events), bad=bad1 + bad2, ends_ok=ends_ok, cont_ok=cont_ok,
                edges_equal=edges1 == edges2, paid=dict(paid), alternating=(dict(alt1), dict(alt2)))


def verdict(d, f, profile):
    rows = {int(t): n for t, n in d['rows'].items()}
    ok = not f['bad'] and f['ends_ok'] and f['cont_ok'] and f['edges_equal'] and f['paid'] == rows
    if profile is not None:
        ok = ok and f['paid'] == profile
    return ok


def main():
    assert not sys.flags.optimize, 'Run without -O'
    argv = sys.argv[1:]
    controls = '--controls' in argv
    profile = None
    word_path, dag_path = [a for a in argv if not a.startswith('--')][:2]
    d = load(word_path)
    if '--profile' in argv:
        p = load(argv[argv.index('--profile') + 1])
        require(all(p[k] == d[k] for k in ('h', 'v', 'R', 'm', 'N', 'W', 'L')), 'profile header')
        profile = {int(t): n for t, n in p['child_multiplicities'].items()}
    h, v = d['h'], d['v']
    m, N = h * h, v * v
    vr = values(d, dag_path)
    f = frames(d)
    rank = sum(t * n for t, n in f['paid'].items())
    require(not f['bad'], 'frame violations, first %s' % (f['bad'][:3],))
    require(f['ends_ok'], 'stage-one endpoints')
    require(f['cont_ok'], 'stage two does not return to the complemented start')
    require(f['edges_equal'], 'stage edge multisets differ')
    require(f['paid'] == {int(t): n for t, n in d['rows'].items()}, 'paid histogram differs from the exported rows')
    require(profile is None or f['paid'] == profile, 'paid histogram differs from the certified profile')
    require(rank == d['W'] * m - N + d['L'], 'rank mass')
    a1, a2 = f['alternating']
    require(a1 == a2, 'alternating counts differ between stages')
    print('PASS deferred complex word: %d ops (%d in phase one), %d deferred slots, %d centres; values replayed '
          'with arbitrary scratch; %d events per invocation per stage, 0 violations, reflection continuous; '
          'paid histogram == %s; alternating residuals per stage %s (one child each)' % (
              vr['ops'], vr['phase_one'], vr['deferred'], vr['centres'], f['events'],
              'certified profile' if profile is not None else 'exported rows',
              ', '.join('rank %d: %d' % kv for kv in sorted(a1.items()))))
    if controls:
        for name in ('phase1-op', 'sigma-full', 'frame', 'drop-copy', 'root'):
            g = frames(mutate(d, name))
            require(not verdict(d, g, profile), 'control %s not rejected' % name)
            print('control %s rejected (%d violations%s%s%s)' % (
                name, len(g['bad']), '' if g['cont_ok'] else ', continuity fails',
                '' if g['ends_ok'] else ', endpoints fail',
                '' if g['paid'] == {int(t): n for t, n in d['rows'].items()} else ', histogram differs'))


if __name__ == '__main__':
    main()
