"""Check the only total-64 profiles that can lower the private bill.

Use rank multiplicities and exact subset means. Do not import the first
checker. The saved geometry proof supplies the support bounds.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import sys
import time

if not __debug__:
    raise SystemExit('Run with assertions enabled.')

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]).resolve()
assert not OUT.exists()
START = time.monotonic()
CAP = (0, 1, 2, 4, 8, 12, 20, 36, 64, 112)
SUPPORT = (0, 53, 76, 92, 100, 106, 109, 111, 112)


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def reject(profile, bounds=SUPPORT, average=True, root_pair=True):
    n = len(profile)
    prefix = [0]
    for rank in profile:
        prefix.append(prefix[-1] + CAP[rank])
    if n < 8:
        return {'reason': 'dimension'}
    if prefix[-1] < 224 - n:
        return {'reason': 'incidence'}
    for dimension in range(1, 9):
        size = n - 8 + dimension
        if prefix[size] < bounds[dimension]:
            return {'reason': 'support', 'dimension': dimension}
    if average:
        for size in range(n - 7, n + 1):
            dimension = size - n + 8
            for rows in range(size + 1, n + 1):
                quotient, remainder = divmod(prefix[rows], 112)
                missing = ((112 - remainder) * choose(rows - quotient, size)
                           + remainder * choose(rows - quotient - 1, size))
                mean = 112 - Fraction(missing, choose(rows, size))
                if mean < bounds[dimension]:
                    return {'reason': 'average', 'dimension': dimension,
                            'subset_size': size, 'selected_rows': rows,
                            'upper_mean': str(mean),
                            'required': bounds[dimension]}
    if root_pair and n == 9 and profile[0] <= 6 and profile[1] <= 7:
        return {'reason': 'short_root_pair', 'upper_root_support': 52,
                'required': 53}
    return None


count = 0
rank_nine = 0
simple_survivors = []
remaining = []


def enumerate_multiplicities(rank, total, multiplicities):
    global count, rank_nine
    if rank == 0:
        if total:
            return
        count += 1
        if not multiplicities[9]:
            return
        rank_nine += 1
        profile = tuple(r for r in range(1, 10)
                        for _ in range(multiplicities[r]))
        if reject(profile, average=False, root_pair=False) is None:
            simple_survivors.append(profile)
            reason = reject(profile)
            assert reason is not None
            remaining.append({'profile': profile, 'rejection': reason})
        return
    for number in range(total // rank + 1):
        multiplicities[rank] = number
        enumerate_multiplicities(rank - 1, total - number * rank,
                                 multiplicities)
    multiplicities[rank] = 0


enumerate_multiplicities(9, 64, [0] * 10)
assert count == 195666 and rank_nine == 79403
assert len(simple_survivors) == 3
assert sum(row['rejection']['reason'] == 'average' for row in remaining) == 2
assert sum(row['rejection']['reason'] == 'short_root_pair'
           for row in remaining) == 1

# The root-pair fact is needed. Omitting it leaves one rank-nine profile.
assert sum(reject(p, root_pair=False) is None for p in simple_survivors) == 1
# The code support fact is needed. This unbuilt profile is cheaper for
# small b but passes the relaxed screen when the first bound is removed.
control = (1,) + (9,) * 7
relaxed = (0, 1) + SUPPORT[2:]
assert reject(control)['reason'] == 'support'
assert reject(control, bounds=relaxed) is None

geometry = ROOT / 'framework/PRIVATE64-GEOMETRY.json'
saved = json.loads(geometry.read_text())
assert tuple(saved['analytic_source_capacities']) == CAP
assert (0,) + tuple(saved['generalized_support_bounds']) == SUPPORT
report = {'status': 'PASS_INDEPENDENT_WEIGHTED_RANK_NINE_EXCLUSION',
          'partitions': count, 'rank_nine_partitions': rank_nine,
          'simple_survivors': remaining,
          'root_pair_omission_survivors': 1,
          'relaxed_support_control': list(control),
          'larger_total_ratio_lower_at_b_1_over_32':
          str(Fraction(65, 64) * (1 - Fraction(1, 256))),
          'geometry_sha256': sha256(geometry.read_bytes()).hexdigest(),
          'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
          'seconds': time.monotonic() - START,
          'scope': 'Independent necessary-condition audit for total64 '
                   'profiles with a rank9 query. Prior sharp64 and geometry '
                   'proofs remain premises. No new circuit or kappa gain.'}
OUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('status', 'partitions',
                                      'rank_nine_partitions', 'seconds')}))
