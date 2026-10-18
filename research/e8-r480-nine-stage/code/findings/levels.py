# Frame-level register visits of a bitE8 word: which registers stand at each frame of each dimension.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: levels.py WORD.json.gz OUT.json
Distinct root-spanned frames of equal dimension are incomparable, so each level is an antichain and a register (whose
frames only climb) stands at most at one frame per level. Reports, per level, the number of helpers that visit it,
and for the cells (level 2) and D6 frames (level 6) the (helpers, sources, targets) visiting each frame."""
import gzip, json, sys
from collections import Counter, defaultdict
import numpy as np

W = json.load(gzip.open(sys.argv[1], 'rt')); V = W['v']; R = W['R']; n = 2 * V + R
fr = [frozenset(x) for x in W['frames']]; L = np.array(W['lines'], dtype=float)
dim = [int(np.linalg.matrix_rank(L[sorted(f)])) if f else 0 for f in fr]
visits = defaultdict(set)                       # register -> frames it stands at (start, gates, final)
for r in range(n): visits[r] |= {W['start'][r], W['final'][r]}
for ph in ('D', 'A', 'B', 'C'):
    for f, d, ss in W[ph]:
        for r in [d] + list(ss): visits[r].add(f)
role = lambda r: 'source' if r < V else ('target' if r < 2 * V else 'helper')
at = defaultdict(Counter)                       # frame -> role counts
per_level = defaultdict(Counter)                # dim -> (helper visits)
for r, fs in visits.items():
    for d in range(9): assert sum(1 for f in fs if dim[f] == d) <= 1 or d in (0, 8), (r, d)   # one frame per level
    for f in fs:
        at[f][role(r)] += 1
        if role(r) == 'helper': per_level[dim[f]][f] += 1
levels = {d: dict(frames=len(per_level[d]), helper_visits=sum(per_level[d].values())) for d in range(1, 8) if per_level[d]}
cells = Counter((at[f]['helper'], at[f]['source'], at[f]['target']) for f in range(len(fr)) if dim[f] == 2)
d6 = Counter((at[f]['helper'], at[f]['source'], at[f]['target']) for f in range(len(fr)) if dim[f] == 6)
out = dict(R=R, levels={str(d): x for d, x in levels.items()},
           cells={'%d,%d,%d' % k: v for k, v in sorted(cells.items())}, d6={'%d,%d,%d' % k: v for k, v in sorted(d6.items())})
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print('R', R, 'helper visits per level', {d: x['helper_visits'] for d, x in levels.items()})
print('cells (helpers,sources,targets) -> count', dict(cells), '; D6 frames', dict(d6))
