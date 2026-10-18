"""Adversarial deletion walks: fix a pivot frame F inside P112, delete random non-pivot live lines one at a time
while (W) and nonempty blocks still hold at F, and run PR1650's criterion (full live family) after each step.
Record the first step at which G or D fails; a 'D' verdict (G passed) is a full-family counterexample."""
import os
import argparse, collections, json, random, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.environ['PR1650_PACKAGE'])  # research/complex-rank8-rigidity-p105 at PR1650 head d960f8a2
import verify as V

PIVOTS = [n for n, m in enumerate(V.FMASK) if not m & V.F0MASK]

def walk(seed):
    rng = random.Random(seed)
    p = rng.choice(PIVOTS); F = V.FRAMES[p]
    X = []
    cand = [i for i in V.P112 if i not in F]
    rng.shuffle(cand)
    events = []
    first = None
    for i in cand:
        r = V.criterion(tuple(X + [i]), F)[0]
        if r in ('W', 'nonempty-blocks'):
            continue  # deleting i breaks the premises at F: keep i
        X.append(i)
        if r is not None:
            rd = V.criterion(tuple(X), F, skip_g=True)[0]  # does D fail too?
            events.append((len(X), r, rd))
            if first is None:
                first = (len(X), r, rd, sorted(X))
    dev = [e for e in events if e[1] in ('D', 'D-kernel-vectors')]
    return dict(seed=seed, pivot=p, final=len(X), first=first, events=events[:5], nevents=len(events), dev=dev[:3], ndev=len(dev), X=sorted(X) if dev else None)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=100); ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--jobs', type=int, default=10); ap.add_argument('--out')
    a = ap.parse_args(); t0 = time.time(); res = []
    c = collections.Counter()
    with ProcessPoolExecutor(a.jobs) as ex:
        for r in ex.map(walk, range(a.start, a.start + a.n)):
            res.append(r)
            c[(r['first'][1], r['first'][2]) if r['first'] else None] += 1
    print(f'walks {a.n} time {time.time()-t0:.1f}s first-failure (criterion, D-only) {dict(c)}')
    print('final deletion counts', collections.Counter(r['final'] for r in res).most_common(8))
    cex = [r for r in res if r['ndev']]
    print('full-family G-pass D-fail first events', len(cex), [ (r['seed'], r['pivot'], r['dev']) for r in cex[:5]])
    if a.out: json.dump(res, open(a.out, 'w'))

if __name__ == '__main__':
    main()
