"""Re-solve a deterministic sample (every k-th entry; n=0 means all) of the stored deletion relaxations and move prices."""
import json, sys
from pathlib import Path
import _paths
import harness as H, frames as F
from word import inline
data = Path(sys.argv[1]); n = int(sys.argv[2])
P = H.Pricer(str(_paths.BASE)); B = P.base['B']
relax = {int(k): v for k, v in json.loads((data / 'relaxation-B.json').read_text()).items()}
items = sorted(relax.items()); step = max(1, len(items) // n) if n else 1
for i, v in items[::step]:
    w1 = H.compile_edits(P.base, dict(delete=[i]))
    g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=P.caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
    assert r['cost'] - P.base_cost == v['delta'], (i, r['cost'] - P.base_cost, v)
print('relaxations re-solved', len(items[::step]))
mv = json.loads((data / 'move-sweep.json').read_text()); step = max(1, len(mv) // n) if n else 1
for x in mv[::step]:
    r = P.price(dict(delete=[x['i']], insert=[(x['p'], list(B[x['i']][:-1]) + [[]])], tail=[], prepend=[]), timeout=300)
    assert r.get('status') == x['status'] and r.get('delta') == x['delta'], (x, r)
print('moves re-priced', len(mv[::step]))
print('PASS_SAMPLE_REPLAY')
