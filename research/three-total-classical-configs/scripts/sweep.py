"""Bounded sweep (writes data/instances.json): structured-coordinate Pappus / Desargues decoder configurations,
CR2 classification (a = 0 2-adic test, then exhaustive support-compatible DFS over GF(2), GF(4), GF(8) with the vendored
#2162 lib/cr2.py), and the exact minimum over all 2^f admissible B (vendored #2111 enumall.c) for non-CR2 instances only.

usage: python3 -I -B scripts/sweep.py SECONDS_BUDGET ENUMALL_BINARY [PER_FRAME]
(recorded run: budget 600, PER_FRAME 2; instance coordinates are recomputed from frame + pairs, not stored)
RNG seed 22.  Frames are visited in a fixed order; the stopping rule is the time budget (recorded in the output).
"""
import json, os, random, subprocess, sys, time
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, 'lib'))
from classical import (pappus, desargues, check_config, frames, transform, setup, dot, odd_diagonal, cost_of, tomat)
from cr2 import realise, cfg_data

SEED = 22
FMAX = 26
DFS_LIMIT = 200000


def overlap(a, b):
    return any(a[j] and b[j] for j in range(3))


def sample_pairs(P2, L2, v, rng, expo):
    n_p, n_l = len(P2), len(L2)
    cand = [(i, k) for i in range(n_p) for k in range(n_l) if dot(P2[i], L2[k]) != 0]
    chosen = []
    while len(chosen) < v:
        opts, wts = [], []
        for (i, k) in cand:
            if (i, k) in chosen:
                continue
            sc = sum(1 for (i2, k2) in chosen if dot(P2[i], L2[k2]) == 0 and overlap(P2[i], L2[k2]))
            sc += sum(1 for (i2, k2) in chosen if dot(P2[i2], L2[k]) == 0 and overlap(P2[i2], L2[k]))
            opts.append((i, k)); wts.append((1 + sc) ** expo)
        chosen.append(rng.choices(opts, weights=wts)[0])
    return chosen


def enumall(binary, v, R, A, free):
    inp = "%d %d\n" % (v, len(free)) + "".join("%d %d\n" % e for e in free) + \
          "".join("%d %s\n%d %s\n" % (len(R[j]), " ".join(map(str, R[j])), len(A[j]), " ".join(map(str, A[j]))) for j in range(3))
    out = subprocess.run([binary, '0'], input=inp, capture_output=True, text=True, check=True, timeout=600).stdout.split()
    best, nm = int(out[0]), int(out[1])
    return best, nm, int(out[3])          # first minimiser's mask g


def classify(P, Q, binary):
    v = len(P)
    R, A, free = setup(P, Q)
    rec = dict(v=v, f=len(free))
    if odd_diagonal(P, Q):
        rec['status'] = 'CR2'; rec['via'] = '2adic-a0'; return rec
    pi, sig = cfg_data(P, Q)
    timeouts = []
    for k in (1, 2, 3):
        r = realise(pi, sig, set(free), k=k, limit=DFS_LIMIT)
        if isinstance(r, dict):
            rec['status'] = 'CR2'; rec['via'] = 'dfs'; rec['k'] = k
            rec['Pt'] = [list(r[('p', t)]) for t in range(v)]; rec['Qt'] = [list(r[('l', t)]) for t in range(v)]
            return rec
        if r == 'timeout':
            timeouts.append(k)
    if timeouts:
        rec['status'] = 'undecided'; rec['dfs_timeout_k'] = timeouts; return rec
    rec['status'] = 'nonCR2'
    if len(free) > FMAX:
        rec['exact'] = 'skipped-f'; return rec
    best, nm, g = enumall(binary, v, R, A, free)
    c = cost_of(P, Q, tomat(g, free, v))
    assert c == best, (c, best)
    rec['exact'] = 'enumall'; rec['min'] = best; rec['nmin'] = nm; rec['witness_g'] = g
    return rec


def main():
    budget = float(sys.argv[1]); binary = sys.argv[2]; per_frame = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    t0 = time.time(); rng = random.Random(SEED)
    confs = [(desargues(), 10), (pappus(), 9)]
    for C, n in confs:
        assert check_config(C, n, 3), C['name']
    out = dict(seed=SEED, fmax=FMAX, dfs_limit=DFS_LIMIT, per_frame=per_frame, budget_s=budget, configs={}, instances=[])
    for C, n in confs:
        out['configs'][C['name']] = dict(points=[list(p) for p in C['points']], pnames=C['pnames'],
                                         lines=[list(l) for l in C['lines']], lnames=C['lnames'], incidences=C['incidences'])
    seen = set(); stopped = False; frames_done = {}
    # interleave: Desargues frames first (primary), then Pappus, round-robin by v
    for C, n in confs:
        frs = frames(C); frames_done[C['name']] = [0, len(frs)]
        for fr in frs:
            if time.time() - t0 > budget:
                stopped = True; break
            P2, L2 = transform(C, fr)
            for rep in range(per_frame):
                v = 6 + (rep % 5)
                expo = 1 + rng.randrange(3)
                pairs = sample_pairs(P2, L2, v, rng, expo)
                key = (C['name'], fr, frozenset(pairs))
                if key in seen:
                    continue
                seen.add(key)
                P = [list(P2[i]) for (i, k) in pairs]; Q = [list(L2[k]) for (i, k) in pairs]
                rec = dict(config=C['name'], frame=list(fr), pairs=[list(x) for x in pairs], expo=expo)
                rec.update(classify(P, Q, binary))
                out['instances'].append(rec)
            frames_done[C['name']][0] += 1
        if stopped:
            break
    out['frames_done'] = frames_done; out['stopped_by_budget'] = stopped; out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(PKG, 'data', 'instances.json'), 'w'), separators=(',', ':'))
    from collections import Counter
    print('frames', frames_done, 'stopped', stopped, 'elapsed', out['elapsed_s'])
    print(Counter((r['config'], r['status'], r.get('via', r.get('exact'))) for r in out['instances']))
    nc = [r for r in out['instances'] if r['status'] == 'nonCR2' and 'min' in r]
    if nc:
        print('min(cost - v) over non-CR2 exact:', min(r['min'] - r['v'] for r in nc))


if __name__ == '__main__':
    main()
