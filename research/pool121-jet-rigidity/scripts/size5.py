"""Exhaustive classification of inclusion-minimal jet-immovable 5-line sub-configurations of the pool -> data/size5.json.
Usage: TMPDIR=/some/tmp python3 -I -B scripts/size5.py   (needs cc; about 9 min: 67 s enumeration, the rest CR2 DFS)
All 5-subsets through one representative of each harmonic-line orbit (order-48 group) are tested; immovable subsets
that contain an immovable 4-subset are dropped (inclusion-minimality); the rest are grouped into orbits.
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, 'lib'))
import jet as A  # noqa: E402
import small  # noqa: E402
import cr2  # noqa: E402  (vendored from #2162)
sys.path.insert(0, os.path.join(HERE, 'scripts'))
from make_data import mincost, orbit_size  # noqa: E402


def main():
    P = A.pool()
    reps, tested, bad = small.check_small(5, minimal_only=True)
    orb = {}
    for S in bad:
        orb.setdefault(A.canon([P[i] for i in S]), []).append(sorted(S))
    binary = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'enumall_pool121')
    subprocess.run(['cc', '-O2', '-o', binary, os.path.join(HERE, 'c', 'enumall.c')], check=True,
                   stderr=subprocess.DEVNULL)
    out = []
    for c in sorted(orb):
        S = min(orb[c])
        L = [P[i] for i in S]
        J = A.Jet(L)
        pi = [A.supp(p) for p, q in L]
        sg = [A.supp(q) for p, q in L]
        E = {(t, s) for (t, s, D) in J.inc}
        cr = 'none over GF(2),GF(4),GF(8),GF(16)'
        for k in (1, 2, 3, 4):
            r = cr2.realise(pi, sg, E, k=k, limit=2 * 10 ** 6)
            if r == 'timeout':
                cr = 'timeout@GF(2^%d)' % k
                break
            if r:
                cr = 'CR2 over GF(2^%d)' % k
                break
        mc, nm = mincost(L, binary)
        out.append({'pool_lines': S, 'free_incidences': len(J.inc), 'harmonic': J.harm, 'immovable': J.immovable(),
                    'orbit_size': orbit_size(L), 'cr2': cr, 'min_cost': mc, 'num_minimisers': nm})
    with open(os.path.join(HERE, 'data', 'size5.json'), 'w') as f:
        json.dump({'harmonic_orbit_reps': reps, 'subsets_tested': tested, 'minimal_immovable_subsets': len(bad),
                   'orbits': out}, f, separators=(',', ':'))
    print('tested', tested, 'minimal immovable', len(bad), 'orbits', len(out))


if __name__ == '__main__':
    main()
