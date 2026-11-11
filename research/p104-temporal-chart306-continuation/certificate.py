"""Exact timed histories with independent final-owned and COPY-zero adjoints.

Causal split: Ali Romman; earlier history and retiming methods: Jerry Chen /
CubeJerry; chart-237 observations: Rohan Arun; executable chart-595 source:
dillona. Guarded suffix adaptation: Clear1nsight, Codex and ChatGPT Pro.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from source import need
from construct import construct, scalar_width
from support import L


def observe(word, hit):
    n = word['public']
    m = n + word['owned_fields']
    events = word['program']
    requests = [defaultdict(set), defaultdict(set)]
    snapshots = [{}, {}]
    for side, name in enumerate(('gathers', 'injections')):
        for x in hit[name]:
            requests[side][x['cut']].add(x['role'])

    def save(side, cut, values):
        for r in requests[side].get(cut, ()):
            snapshots[side][cut, r] = dict(values[r])

    rows = [{i: Q(1)} if i < n else {} for i in range(m)]
    save(0, 0, rows)
    for i, e in enumerate(events):
        op, r = e[:2]
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {k: Q(e[-2])*q for k, q in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            if op == 'COPY':
                need(not rows[r], 'Original COPY destination must be zero')
            L.add(rows[r], rows[e[2]], Q(e[-2]))
        save(0, i+1, rows)

    # Coordinates [0,m) are all final roles, including owned fields. The
    # unique coordinate m+i measures the destination just before COPY i.
    cols = [{i: Q(1)} for i in range(m)]
    save(1, len(events), cols)
    for i in reversed(range(len(events))):
        e = events[i]
        op, r = e[:2]
        if op in ('INIT', 'CLEAR'):
            cols[r] = {}
        elif op == 'SCALE':
            cols[r] = {k: Q(e[-2])*q for k, q in cols[r].items()}
        elif op in ('ADD', 'COPY'):
            L.add(cols[e[2]], cols[r], Q(e[-2]))
            if op == 'COPY':
                cols[r] = {m+i: Q(1)}
        save(1, i, cols)
    return snapshots


def check(hit, snapshots):
    vectors = {}
    for side, field, target in ((0, 'gathers', 'c'), (1, 'injections', 'd')):
        total, seen = {}, set()
        for x in hit[field]:
            key = x['cut'], x['role']
            need(key in snapshots[side] and key not in seen, 'Distinct source observation')
            seen.add(key)
            need(x['frame'] == hit['frame'], 'One accumulator frame')
            need(x['cut'] <= hit['cut'] if side == 0 else x['cut'] >= hit['cut'], 'Causal chronology')
            q = Q(x['coefficient'])
            need(q != 0, 'Nonzero timed coefficient')
            L.add(total, snapshots[side][key], q)
        want = {int(k): Q(q) for k, q in hit[target].items()}
        need(total == want, 'All coefficients, including outside and guard coordinates, for ' + target)
        vectors[target] = {str(k): str(v) for k, v in sorted(total.items())}
    c, d = ({int(k): Q(q) for k, q in vectors[x].items()} for x in ('c', 'd'))
    need(sum(q*d.get(r, 0) for r, q in c.items()) == 1, 'Unit pairing')
    return dict(status='PASS_EXACT_GUARDED_TIMED_OBSERVATIONS', gather_count=len(hit['gathers']),
                injection_count=len(hit['injections']), latest_gather=max(x['cut'] for x in hit['gathers']),
                retirement_cut=hit['cut'], earliest_injection=min(x['cut'] for x in hit['injections']),
                vectors=vectors, boundary_pairing='1')


def rejected(action):
    try:
        action()
    except (AssertionError, ValueError):
        return True
    raise ValueError('Corruption accepted')


def controls(word, hit, paths, snapshots=None):
    snapshots = observe(word, hit) if snapshots is None else snapshots
    check(hit, snapshots)
    results = {}
    for field in ('gathers', 'injections'):
        bad = deepcopy(hit)
        bad[field][0]['coefficient'] = str(2*Q(bad[field][0]['coefficient']))
        results['wrong_'+field+'_coefficient'] = rejected(lambda: check(bad, snapshots))
        bad = deepcopy(hit)
        bad[field].pop(0)
        results['omitted_'+field+'_observation'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['cut'] = max(x['cut'] for x in bad['gathers'])-1
    results['retirement_before_last_gather'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['injections'][0]['cut'] = hit['cut']-1
    results['injection_before_retirement'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['paid_delta'] = {}
    results['omitted_paid_midpoint_cost'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['path']['hi'] = bad['path']['moves'][0]
    results['incomplete_paid_path'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['ranks'] = list(reversed(bad['ranks']))
    results['wrong_productive_ranks'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['gathers'][0]['cut'] = hit['cut']+1
    results['gather_after_retirement'] = rejected(lambda: construct(word, bad, paths))
    toy = {'public': 1, 'owned_fields': 1,
           'program': [['INIT', 1, 0], ['COPY', 1, 0, '1', 0], ['CLEAR', 1, 0]]}
    toy_hit = {'gathers': [], 'injections': [{'cut': 1, 'role': 1}]}
    _, cols = observe(toy, toy_hit)
    # This perturbation is invisible at the final output because of COPY
    # and CLEAR; it is nevertheless forbidden at the interior COPY.
    need(cols == {(1, 1): {3: Q(1)}}, 'COPY-zero control must see erased perturbation')
    results['output_invisible_copy_violation_detected'] = True
    results['oversized_scalar_numerator_rejected'] = rejected(
        lambda: scalar_width({'program': [['ADD', 0, 1, str(2**24), 0]]}))
    return results
