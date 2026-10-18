"""Per-instance CR2 classification on the one coordinate system without a frame-universal certificate (data/special.json:
Pappus realisation with A0B0C0 collinear and l, m, pap concurrent, identity coordinates).  Samples decoder configurations
(v = 6..10, RNG seed 22, incidence-biased as in scripts/sweep.py), classifies them with the a = 0 2-adic test and the
vendored cr2.py DFS over GF(2), GF(4), GF(8); non-CR2 instances with f <= 26 get the exact minimum over all 2^f admissible
B from the vendored enumall (writes data/special_instances.json).

usage: python3 -I -B scripts/special_instances.py N_SAMPLES ENUMALL_BINARY SECONDS_BUDGET
"""
import json, os, random, sys, time
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, 'lib')); sys.path.insert(0, os.path.join(PKG, 'scripts'))
from sweep import sample_pairs, classify


def main():
    N = int(sys.argv[1]); binary = sys.argv[2]; budget = float(sys.argv[3]); t0 = time.time()
    S = json.load(open(os.path.join(PKG, 'data', 'special.json')))
    tgt = [r for r in S['configs']['pappus']['realisations'] if any(f['k'] is None for f in r['frames'])]
    assert len(tgt) == 1 and [f['frame'] for f in tgt[0]['frames'] if f['k'] is None] == [['I']]
    P2 = [tuple(p) for p in tgt[0]['points']]; L2 = [tuple(l) for l in tgt[0]['lines']]
    rng = random.Random(22); seen = set(); out = dict(seed=22, params=tgt[0]['params'], n_requested=N, instances=[])
    for rep in range(N):
        if time.time() - t0 > budget:
            break
        v = 6 + (rep % 5); expo = 1 + rng.randrange(4)
        pairs = sample_pairs(P2, L2, v, rng, expo)
        key = frozenset(pairs)
        if key in seen:
            continue
        seen.add(key)
        P = [list(P2[i]) for (i, k) in pairs]; Q = [list(L2[k]) for (i, k) in pairs]
        rec = dict(pairs=[list(x) for x in pairs], expo=expo); rec.update(classify(P, Q, binary))
        out['instances'].append(rec)
    out['elapsed_s'] = round(time.time() - t0, 1); out['attempts'] = rep + 1
    json.dump(out, open(os.path.join(PKG, 'data', 'special_instances.json'), 'w'), separators=(',', ':'))
    from collections import Counter
    print('instances', len(out['instances']), 'elapsed', out['elapsed_s'])
    print(Counter((r['status'], r.get('via', r.get('exact'))) for r in out['instances']))
    nc = [r for r in out['instances'] if r['status'] == 'nonCR2' and 'min' in r]
    print('non-CR2 exact:', len(nc), 'min(cost - v):', min((r['min'] - r['v'] for r in nc), default=None))
    print(sorted(Counter((r['v'], r['f'], r['min']) for r in nc).items()))


if __name__ == '__main__':
    main()
