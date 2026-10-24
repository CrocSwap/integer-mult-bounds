"""Screen literal TARGET cuts before constructing a new center schedule.

The screen gives a lower bound for one saved copy per center. It keeps the
actual B decoder and all TARGET frame changes. It omits positive storage,
owner, coefficient and wrapper costs. It does not admit a new supplier.
Prepared with OpenAI Codex assistance. See HANDOFF.md for source credits.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time

if not __debug__:
    raise SystemExit('Run with assertions enabled.')

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--word', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
word_path = args.word.resolve()
w = json.loads(gzip.decompress(word_path.read_bytes()))
v, n = w['v'], 2*w['v']+w['R']
assert v == 112 and w['h'] == 9 and n == 728
assert not w['target_levels']
assert all(not v <= e[2] < 2*v for e in w['B']
           if e[0] == 'add' and not v <= e[1] < 2*v)
frames = w['frames']
assert len(frames[1]) == 9
assert all(len(frames[f]) == 8 for f in w['center_frames'])


def binary_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            k = x.bit_length()-1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return len(pivots)


assert all(binary_rank(frame) == len(frame) for frame in frames)
center_at = {r: i for i, r in enumerate(w['centers'])}
z = [[Q(0) for _ in range(8)] for _ in range(v)]
for e in w['cut']:
    assert e[0] == 'add' and v <= e[1] < 2*v and e[2] in center_at
    z[e[1]-v][center_at[e[2]]] += Q(e[3], e[4])
original = [row.copy() for row in z]
current = w['start'].copy()
for e in w['A']:
    for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
        current[r] = e[-1]
assert all(current[v+t] == 0 for t in range(v))
assert [current[r] for r in w['centers']] == w['center_frames']
distances = [[2*binary_rank(frames[f] + frames[g])-len(frames[f])-len(frames[g])
              for g in range(len(frames))] for f in w['center_frames']]
best = [None]*8
productive_best = [None]*8
common_best = None
histograms = [Counter() for _ in range(8)]
cut_count = 0
target_climb_cuts = 0
started = time.monotonic()


@lru_cache(None)
def distance(f, g):
    return 2*binary_rank(frames[f]+frames[g])-len(frames[f])-len(frames[g])


@lru_cache(None)
def spanning_tree_lower(start, used):
    vertices = set(used)-{start}
    nearest = {f: distance(start, f) for f in vertices}
    total = 0
    while nearest:
        f = min(nearest, key=lambda x: (nearest[x], x))
        total += nearest.pop(f)
        for g in nearest:
            nearest[g] = min(nearest[g], distance(f, g))
    return total


def inspect(index, stage='after_scalar', register=None):
    global cut_count, common_best
    costs, descriptions = [], []
    for k in range(8):
        support = [t for t in range(v) if z[t][k]]
        assert support
        used = sorted({current[v+t] for t in support})
        # A copy path visits its start and every served frame. Remove any
        # other vertices by the triangle inequality. A spanning tree on
        # the remaining vertices costs no more than that path.
        endpoint_lower = max(distances[k][f] for f in used)
        lower = spanning_tree_lower(w['center_frames'][k], tuple(used))
        assert lower >= endpoint_lower
        # Grant a free exchange into a productive FULL9-exit carrier at
        # the same frame8 cut. Its route must also reach FULL9. Its old
        # remaining completion costs one rank unit. A route through any
        # served frame gives another exact lower bound. Total path rank
        # has the parity of the endpoint dimension difference.
        full_route = max(spanning_tree_lower(w['center_frames'][k], tuple(sorted(set(used)|{1}))),
                         max(distances[k][f]+9-len(frames[f]) for f in used))
        full_route += (1-full_route)%2
        productive = dict(B_prefix_length=index, stage=stage, climbed_register=register,
                          lower_route_rank_to_FULL9=full_route,
                          old_remaining_completion_rank=1,
                          lower_extra_rank=full_route-1)
        if productive_best[k] is None or full_route < productive_best[k]['lower_route_rank_to_FULL9']:
            productive_best[k] = productive
        costs.append(lower)
        histograms[k][lower] += 1
        detail = dict(B_prefix_length=index, stage=stage, climbed_register=register,
                      lower_copy_transition_rank=lower,
                      endpoint_distance_lower=endpoint_lower,
                      target_support_size=len(support), served_frame_ids=used,
                      served_frame_rank_histogram=dict(sorted(Counter(len(frames[f])
                                                                  for f in used).items())),
                      support=[dict(target=t, frame=current[v+t], coefficient=str(z[t][k]))
                               for t in support])
        descriptions.append(detail)
        if best[k] is None or lower < best[k]['lower_copy_transition_rank']:
            best[k] = detail
    total = sum(costs)
    if common_best is None or total < common_best['lower_copy_transition_rank_sum']:
        common_best = dict(B_prefix_length=index, stage=stage, climbed_register=register,
                           lower_copy_transition_rank_sum=total,
                           center_lower_bounds=costs,
                           target_support_sizes=[x['target_support_size'] for x in descriptions])
    cut_count += 1


inspect(0, 'before_B')
for index, e in enumerate(w['B'], 1):
    touched = [e[1]] + ([e[2]] if e[0] == 'add' else [])
    for r in touched:
        changed = current[r] != e[-1]
        current[r] = e[-1]
        if changed and v <= r < 2*v:
            target_climb_cuts += 1
            inspect(index-1, 'after_target_climb_before_scalar', r)
    if v <= e[1] < 2*v:
        dst = e[1]-v
        if e[0] == 'scale':
            q = Q(e[2], e[3])
            z[dst] = [q*x for x in z[dst]]
        elif v <= e[2] < 2*v:
            q = Q(e[3], e[4])
            src = z[e[2]-v]
            z[dst] = [x+q*y for x, y in zip(z[dst], src)]
    inspect(index)
independent_lower = sum(x['lower_copy_transition_rank'] for x in best)
assert cut_count == len(w['B'])+target_climb_cuts+1
assert all(row != [] for row in z)
report = dict(status='PASS_EXACT_DELAYED_INJECTION_NECESSARY_COST_SCREEN',
              source_PR=564, source_head='c18417b02b80594b2ca1c8c21185d28befafc935',
              word_sha256=hashlib.sha256(word_path.read_bytes()).hexdigest(),
              word_payload_sha256=hashlib.sha256(gzip.decompress(word_path.read_bytes())).hexdigest(),
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              B_gates=len(w['B']), TARGET_climb_cuts=target_climb_cuts,
              cuts_checked=cut_count,
              old_private_transition_rank_sum=64,
              lower_bound_with_independent_center_cuts=independent_lower,
              best_common_cut=common_best, best_center_cuts=best,
              productive_carrier_best_cuts=productive_best,
              productive_carrier_extra_rank_lower_sum=sum(x['lower_extra_rank'] for x in productive_best),
              lower_bound_histograms=[dict(sorted(h.items())) for h in histograms],
              seconds=time.monotonic()-started,
              argument='The B background never reads a TARGET. Its TARGET block is invertible, since each TARGET-only add/scale is invertible. For the same saved center value, moving injection through a B prefix multiplies the injection column by that prefix TARGET block. All other columns stay fixed. Any literal copy path must visit the actual frames of every nonzero transported target. The canonical transition distance is dimF+dimG-2dim(F intersect G). Its triangle inequality permits removal of intermediate frames and gives a minimum spanning tree on the start and served frames as a lower bound. Separate center cuts, arbitrary target order and arbitrary intermediate frames are granted. Holding copies, physical owners, ordinary operations, wrappers and fresh dirt interfaces have no negative price and are omitted.',
              scope='Each original center value is held without changing its scalar value and injected at one literal B cut. The private case uses one copy. The productive case grants a free same-frame exchange into a carrier that has frame8 at the old cut and must exit FULL9; its old remaining rank1 completion is credited. The unchanged B word and actual TARGET frames remain. The productive scalar exchange and arbitrary-dirt endpoint are not asserted to exist. This does not exclude split injections, new TARGET words, a joint productive operator, a new SOURCE basis or another controller. A lower bound below64 is a screen only, not a verified gain.')
args.out.resolve().parent.mkdir(parents=True, exist_ok=True)
args.out.resolve().write_text(json.dumps(report, indent=2)+'\n')
print(report['status'], 'cuts', cut_count, 'independent lower', independent_lower,
      'common lower', common_best['lower_copy_transition_rank_sum'], flush=True)
