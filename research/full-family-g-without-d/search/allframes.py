"""Full-live-family (G)/(D) census: for each unit X (deleted lines besides FRAME0), run PR1650's criterion at
EVERY live frame and tally reasons. A counterexample is a frame failing D or D-kernel-vectors (G already passed)."""
import argparse, collections, gzip, json, os, random, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.environ['PR1650_PACKAGE'])  # research/complex-rank8-rigidity-p105 at PR1650 head d960f8a2
import verify as V

def unit(X):
    xm = V.F0MASK | sum(1 << i for i in X)
    tally = collections.Counter(); bad = []
    for n, m in enumerate(V.FMASK):
        if m & xm:
            continue
        r = V.criterion(tuple(X), V.FRAMES[n])[0]
        tally[r] += 1
        if r in ('D', 'D-kernel-vectors'):
            bad.append((list(X), n, r))
    return tally, bad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('level'); ap.add_argument('--jobs', type=int, default=10)
    ap.add_argument('--sample', type=int, default=0); ap.add_argument('--size', type=int, default=8)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out')
    a = ap.parse_args()
    if a.level == 'random':
        rng = random.Random(a.seed)
        units = [sorted(rng.sample(V.P112, a.size)) for _ in range(a.sample)]
    else:
        units = json.loads(gzip.decompress(V.UNITS_FILE.read_bytes()))[a.level]
        units = [u[:7] if a.level == 'p105' else u for u in units]
        if a.sample:
            units = random.Random(a.seed).sample(units, a.sample)
    t0 = time.time(); tot = collections.Counter(); bads = []; passing = []
    with ProcessPoolExecutor(a.jobs) as ex:
        for t, b in ex.map(unit, units, chunksize=8):
            tot.update(t); bads += b; passing.append(t[None])
    print(f'{a.level} units {len(units)} time {time.time()-t0:.1f}s reasons {dict(sorted(tot.items(), key=lambda kv: str(kv[0])))}')
    print(f'units with no passing frame {sum(p == 0 for p in passing)}; min/max passing frames {min(passing)}/{max(passing)}')
    print(f'G-passing D-failures {len(bads)}', bads[:10])
    if a.out:
        json.dump(dict(level=a.level, units=len(units), reasons={str(k): v for k, v in tot.items()}, bad=bads), open(a.out, 'w'))

if __name__ == '__main__':
    main()
