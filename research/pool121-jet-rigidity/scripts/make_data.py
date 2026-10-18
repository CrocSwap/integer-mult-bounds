"""Regenerate data/flows.json, data/atoms.json and data/q4.json (exploratory search; verify.py re-checks the output).
Usage: python3 -I -B scripts/make_data.py [--orders N] [--pool-orders M]
Search domain: inclusion-minimal sub-configurations S of the 121-line pool on which Corollary J fails
(some harmonic line of S is immovable for (J1) of S). Seeded greedy single-pass line deletion (seed 43), starting
(i) from the lines touched by a Lemma F flow of each harmonic line of the pool (N orders each) and
(ii) from the whole pool (M orders); plus (iii) the exhaustive list of immovable 4-line sub-configurations
(lib/small.py, which also shows that none has <= 3 lines). Orbits are taken modulo the order-48 signed-permutation group.
A greedy pass yields an inclusion-minimal set because immovability is upward closed (a flow of S is a flow of every
S' containing S). This is a search: atoms not reached are not excluded.
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
import json, os, random, subprocess, sys, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from jet import Jet, pool, canon, signed_perms, act, normalise, supp  # noqa: E402
import cr2  # noqa: E402  (vendored from #2162)

ORDERS = int(sys.argv[sys.argv.index('--orders') + 1]) if '--orders' in sys.argv else 40
PORDERS = int(sys.argv[sys.argv.index('--pool-orders') + 1]) if '--pool-orders' in sys.argv else 8
ENUM_CAP = 26
P = pool()
J = Jet(P)
J.eliminate()


def fails(S):
    return len(Jet([P[i] for i in S]).immovable()) > 0


def greedy(start, rng):
    order = sorted(start)
    rng.shuffle(order)
    cur = set(start)
    for u in order:
        if fails(cur - {u}):
            cur -= {u}
    return sorted(cur)


def orbit_size(lines):
    imgs = set()
    for g in signed_perms():
        imgs.add(tuple(sorted((normalise(act(g, p)), normalise(act(g, q))) for p, q in lines)))
    return len(imgs)


def mincost(lines, binary):
    Jt = Jet(lines)
    v = Jt.v
    R = [[t for t in range(v) if lines[t][0][j]] for j in range(3)]
    A = [[s for s in range(v) if lines[s][1][j]] for j in range(3)]
    inp = '%d %d\n' % (v, len(Jt.inc)) + ''.join('%d %d\n' % (t, s) for (t, s, D) in Jt.inc)
    for j in range(3):
        inp += '%d %s\n%d %s\n' % (len(R[j]), ' '.join(map(str, R[j])), len(A[j]), ' '.join(map(str, A[j])))
    out = subprocess.run([binary, '0'], input=inp, capture_output=True, text=True, timeout=120).stdout.split()
    return int(out[0]), int(out[1])


def main():
    t0 = time.time()
    flows = {}
    for t in J.harm:
        fl = J.flow(t)
        flows[str(t)] = [[J.inc[k][0], J.inc[k][1]] for k in fl]
    rng = random.Random(43)
    atoms = {}
    starts = []
    for t in J.harm:
        S = {t}
        for (a, b) in flows[str(t)]:
            S |= {a, b}
        starts += [S] * ORDERS
    starts += [set(range(len(P)))] * PORDERS
    for S in starts:
        A = greedy(S, rng)
        c = canon([P[i] for i in A])
        atoms.setdefault(c, A)
    # exhaustive part: all immovable 4-line sub-configurations (lib/small.py); none exist with <= 3 lines
    from small import check_small
    reps, tested, bad = check_small(4)
    for S in bad:
        atoms.setdefault(canon([P[i] for i in S]), sorted(S))
    binary = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'enumall_pool121')
    subprocess.run(['cc', '-O2', '-o', binary, os.path.join(HERE, 'c', 'enumall.c')], check=True)
    out = []
    for c, A in sorted(atoms.items(), key=lambda x: (len(x[1]), x[1])):
        lines = [P[i] for i in A]
        Jt = Jet(lines)
        imm = Jt.immovable()
        pi = [supp(p) for p, q in lines]
        sig = [supp(q) for p, q in lines]
        E = {(t, s) for (t, s, D) in Jt.inc}
        cr = None
        for k in (1, 2, 3, 4):
            r = cr2.realise(pi, sig, E, k=k, limit=2 * 10 ** 6)
            if r == 'timeout':
                cr = 'timeout@GF(2^%d)' % k
                break
            if r:
                cr = {'k': k, 'P': [list(r[('p', t)]) for t in range(len(lines))],
                      'Q': [list(r[('l', t)]) for t in range(len(lines))]}
                break
        rec = {'pool_lines': A, 'lines': [[list(p), list(q)] for p, q in lines], 'v': len(lines),
               'free_incidences': len(Jt.inc), 'harmonic': Jt.harm, 'immovable': imm,
               'flow': {str(t): [[Jt.inc[k][0], Jt.inc[k][1]] for k in Jt.flow(t)] for t in imm},
               'orbit_size': orbit_size(lines), 'cr2': cr if cr is not None else 'none over GF(2),GF(4),GF(8),GF(16)'}
        if len(Jt.inc) <= ENUM_CAP:
            rec['min_cost'], rec['num_minimisers'] = mincost(lines, binary)
        out.append(rec)
        print(rec['v'], rec['free_incidences'], imm, rec['orbit_size'], rec.get('min_cost'),
              rec['cr2'] if isinstance(rec['cr2'], str) else 'CR2 GF(2^%d)' % rec['cr2']['k'], flush=True)
    meta = {'seed': 43, 'orders_per_flow_start': ORDERS, 'pool_orders': PORDERS, 'starts': len(starts),
            'exhaustive_size4': {'harmonic_orbit_reps': reps, 'subsets_tested': tested, 'immovable': [list(b) for b in bad]},
            'distinct_orbits': len(out), 'enum_cap_free_incidences': ENUM_CAP}
    with open(os.path.join(HERE, 'data', 'flows.json'), 'w') as f:
        json.dump({'pool_rank': J.eliminate(), 'flows': flows}, f, separators=(',', ':'))
    with open(os.path.join(HERE, 'data', 'atoms.json'), 'w') as f:
        json.dump({'meta': meta, 'atoms': out}, f, indent=0, separators=(',', ':'))
    print(meta)
    # Q4 (time-boxed search): greedy insertion of lines in 16 seeded orders (odd passes: harmonic lines first),
    # keeping S Corollary-J certifiable (no immovable harmonic line). A failed search for larger S, not an optimum.
    H = set(J.harm)
    def ok(S):
        return not Jet([P[i] for i in sorted(S)]).immovable()
    rng = random.Random(43)
    best, sizes = None, []
    for rep in range(16):
        order = list(range(len(P)))
        rng.shuffle(order)
        if rep % 2:
            order = [h for h in order if h in H] + [u for u in order if u not in H]
        S = set()
        for u in order:
            if ok(S | {u}):
                S.add(u)
        sizes.append(len(S))
        if best is None or len(S) > len(best):
            best = set(S)
    with open(os.path.join(HERE, 'data', 'q4.json'), 'w') as f:
        json.dump({'seed': 43, 'passes': 16, 'pass_sizes': sizes, 'best': sorted(best),
                   'best_harmonic': len(best & H)}, f, separators=(',', ':'))
    print('Q4 pass sizes', sizes, 'best', len(best))


if __name__ == '__main__':
    main()
