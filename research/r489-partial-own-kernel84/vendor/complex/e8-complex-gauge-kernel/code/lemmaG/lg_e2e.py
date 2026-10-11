# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""End-to-end exact identity of the full emitted local program (both orientations) on >= 256 random basis columns, structured
columns (every entering helper twice, every target with a nonzero level, every centre register, every source/target port) and
dense columns (every register dirty with random Gaussian integers simultaneously).  Transitions, data adapters and wrappers are
executed from their serialized recipes; the expected transform is computed from definitions (lg_phys.expected).
usage: lg_e2e.py VARIANT [n_random] [seed]"""
import sys, json, time, random
import numpy as np
from lg_lib import load
from lg_phys import Model, run, expected, compare
from gd import GD
import os
SP = os.environ['LG_BASE']          # the output directory of verify.py: <SP>/<variant>/{split-centres,hosted}
name = sys.argv[1]; nr = int(sys.argv[2]) if len(sys.argv) > 2 else 256; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
d = load(f'{SP}/{name}'); m = Model(d); c = d['c']; v = c['v']; rng = random.Random(seed)
cols = [('random', rng.randrange(m.n), rng.randrange(512)) for _ in range(nr)]
ent = [r for r in range(2 * v, m.n) if c['start'][r] != 0]
cols += [('entering', r, b) for r in ent for b in (0, rng.randrange(1, 512))]
cols += [('target_level', v + int(t), rng.randrange(512)) for t in c.get('target_levels', {})]
cols += [('centre', r, rng.randrange(512)) for r in c['centers']]
cols += [('port', r, rng.randrange(512)) for r in range(2 * v)]
B = 32; rep = {'variant': name, 'seed': seed, 'columns': len(cols), 'kinds': {}, 'batches': 0, 'failures': [], 'dense': 0}
for k in set(x[0] for x in cols): rep['kinds'][k] = sum(1 for x in cols if x[0] == k)
t0 = time.time()
def check(init, label):
    for o in ('forward', 'backward'):
        got = run(m, d['progs'][o], init); exp = expected(m, init, o == 'backward')
        bad, left = compare(m, got, exp)
        if bad or left: rep['failures'].append((label, o, bad[:10], [str(x) for x in left]))
for i in range(0, len(cols), B):
    chunk = cols[i:i + B]; init = {}
    for ci, (_, r, b) in enumerate(chunk): init.setdefault(('L', r), GD.zeros(len(chunk))).re[b, ci] = 1
    check(init, f'batch{i // B}'); rep['batches'] += 1
    print(name, 'batch', i // B, 'failures so far', len(rep['failures']), round(time.time() - t0), flush=True)
nprng = np.random.default_rng(seed)
for j in range(2):                      # dense: every register dirty at once, 4 independent columns per run
    k = 4; init = {('L', r): GD(nprng.integers(-1000, 1001, (512, k)).astype(np.int64), nprng.integers(-1000, 1001, (512, k)).astype(np.int64), 0) for r in range(m.n)}
    check(init, f'dense{j}'); rep['dense'] += k
    print(name, 'dense', j, 'failures so far', len(rep['failures']), round(time.time() - t0), flush=True)
rep['seconds'] = round(time.time() - t0, 1); rep['status'] = 'PASS' if not rep['failures'] else 'FAIL'
json.dump(rep, open(f'E2E-{name}.json', 'w'), indent=1); print(name, rep['status'], rep['columns'], 'basis columns +', rep['dense'], 'dense', rep['seconds'], 's')
