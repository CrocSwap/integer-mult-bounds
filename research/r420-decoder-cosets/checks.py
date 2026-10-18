# Apache-2.0; cxnmai with substantial OpenAI assistance.
"""Set-valued dirty-input replay, paths, positive envelopes and controls."""
import copy
from model import INDEX, counts


def replay(w):
    n, v = 2*w['v']+w['R'], w['v']
    values = [{r} for r in range(n)]
    paths = [[f] for f in w['start']]
    positive = [1]*n
    peak = 1
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            gates = [[0, v+t, [w['ret'][k] for k in row]]
                     for t, row in enumerate(w['scatter'])]
        else:
            gates = w[section]
        for frame, dst, srcs in gates:
            if section != 'scatter':
                assert dst not in srcs and len(srcs) == len(set(srcs))
                for r in [dst]+srcs:
                    if paths[r][-1] != frame:
                        paths[r].append(frame)
            for src in srcs:
                values[dst] ^= values[src]
                positive[dst] += positive[src]
                peak = max(peak, positive[dst])
    for r, f in enumerate(w['final']):
        if paths[r][-1] != f:
            paths[r].append(f)
    expected = [{r, r-v} if v <= r < 2*v else {r} for r in range(n)]
    assert values == expected, 'dirty-input map mismatch'
    return paths, peak


def controls(original, candidate):
    rejected = []
    variants = {}
    bad = copy.deepcopy(candidate)
    bad['D'] = original['D']
    variants['stale_compensation'] = bad
    bad = copy.deepcopy(candidate)
    bad['C'] = original['C']
    variants['stale_cleanup'] = bad
    bad = copy.deepcopy(candidate)
    bad['D'][0][2].pop()
    variants['missing_compensation_read'] = bad
    bad = copy.deepcopy(candidate)
    bad['C'].pop()
    variants['missing_cleanup_gate'] = bad
    bad = copy.deepcopy(candidate)
    bad['A'][-9+INDEX][2].pop()
    bad['C'] = [[1, d, ss[:]] for _, d, ss in reversed(bad['A']+bad['B'])
                if not 120 <= d < 240]
    variants['corrupt_total_with_matched_cleanup'] = bad
    for name, bad in variants.items():
        try:
            replay(bad)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('control accepted: '+name)
    return rejected
