"""A finite, charged execution of the compatible shear endpoint in PR #6658."""
from fractions import Fraction


def replay(raw_cuts, replication, parent, records, fee):
    """Apply each invocation at its own cut and count the specified unit fees."""
    charges = adds = calls = 0
    counts_by_cut = []
    for (q, rows), counts in zip(raw_cuts, records, strict=True):
        size = q * replication
        xs = [17*i - 13*q for i in range(size)]
        ys = [3*i + q + 1 for i in range(size)]
        dirty = [v*v - 7 for v in xs]
        expected = ([x+y for x, y in zip(xs, ys, strict=True)], ys.copy(), dirty.copy())
        pos = 0
        per_cut_calls = 0
        for (width, price), count in zip(rows, counts, strict=True):
            if price != width + 1 or type(count) is not int or count < 0:
                raise ValueError("expected a whole invocation at the fixed unit fee")
            for _ in range(count):
                end = pos + width
                if end > size:
                    raise ValueError("invocation crosses chronological cut")
                calls += 1
                per_cut_calls += 1
                charges += 1
                for i in range(pos, end):
                    xs[i] += ys[i]
                    charges += 1
                    adds += 1
                pos = end
        if pos != size or (xs, ys, dirty) != expected:
            raise ValueError("incomplete chronological endpoint")
        counts_by_cut.append(per_cut_calls)
    if fee != Fraction(charges, parent*replication):
        raise ValueError("observed dispatch and addition bill")
    return adds, calls, counts_by_cut


def run_schedules(cases, results):
    instances = adds = calls = 0
    for case in cases:
        if case['name'] not in ('source-6658-N12', 'fixed-fee-N12'):
            continue
        raw = case['cuts']
        for row in results[case['name']]['records']:
            n, k, _ = replay(raw, row['a'], case['parent'], row['counts'], Fraction(row['cost']))
            adds += n
            calls += k
            instances += 1
    # Two width-two jobs in aggregate would fit one invocation, but placing it
    # at the first one-job cut crosses that cut, even if a pooled cost would match.
    split = [(1, [(2, 3)]), (1, [(2, 3)])]
    try:
        replay(split, 1, 1, [[1], [0]], Fraction(3))
    except ValueError as exc:
        if str(exc) != "invocation crosses chronological cut":
            raise
    else:
        raise ValueError("pooled execution accepted")
    return dict(schedules=instances, unit_additions=adds, unit_dispatches=calls,
                pooled_counterexample_rejected=True)
