"""Recompute the headline counts of RESULTS.json from the data files."""
import json, sys, collections
from pathlib import Path
P = Path(sys.argv[1]); R = json.loads((P / 'RESULTS.json').read_text())
relax = json.loads((P / 'data/relaxation-B.json').read_text()); mv = json.loads((P / 'data/move-sweep.json').read_text())
comp = json.loads((P / 'data/compensation-searches.json').read_text())
gains = [v['delta'] for v in relax.values() if v.get('delta', 0) < 0]
assert R['b_deletion_relaxation']['relaxed'] == len(relax) == 1797 and R['b_deletion_relaxation']['with_gain'] == len(gains) == 1002
assert R['b_deletion_relaxation']['gain_histogram'] == {str(k): v for k, v in sorted(collections.Counter(gains).items())}
s = R['exact_single_move_sweep']
assert s['positions'] == len(mv) and s['gains'] == 0 == sum(1 for x in mv if (x['delta'] or 0) < 0) and s['losses'] == 0
assert s['neutral'] + s['infeasible'] == len(mv)
assert R['compensation_searches']['records'] == len(comp) and R['compensation_searches']['negative_delta_found'] == 0
print('PASS_RESULTS_CONSISTENT', len(relax), len(mv), len(comp))
