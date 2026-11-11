"""Exact timed observation certificate; no discovery code is trusted.

Causal-history identity: Ali Romman. Temporal coefficient methods and retiming:
Jerry Chen / CubeJerry; complete kernels: Matarener. Implementation for dillona
with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from support import L
from construct import construct


def observe(word, hit):
    n = word['public']
    N = n+word['owned_fields']
    requests = [defaultdict(set), defaultdict(set)]
    for side, field in enumerate(('gathers', 'injections')):
        for obs in hit[field]:
            requests[side][obs['cut']].add(obs['role'])
    snapshots = [{}, {}]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cols = [{r: Q(1)} if r < n else {} for r in range(N)]
    events = word['program']
    def save(side, cut, values):
        for r in requests[side].get(cut, ()):
            snapshots[side][cut, r] = dict(values[r])
    save(0, 0, rows)
    for i, e in enumerate(events):
        op, r = e[:2]
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {k: Q(e[-2])*q for k, q in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            if op == 'COPY':
                L.need(not rows[r], 'Every source COPY destination is ideal zero')
            L.add(rows[r], rows[e[2]], Q(e[-2]))
        save(0, i+1, rows)
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
                cols[r] = {}
        save(1, i, cols)
    return snapshots


def check(hit, snapshots):
    result = {}
    for side, field, target in ((0, 'gathers', 'c'), (1, 'injections', 'd')):
        total = {}
        seen = set()
        for obs in hit[field]:
            key = obs['cut'], obs['role']
            L.need(key in snapshots[side] and key not in seen, 'Distinct authenticated source observation')
            seen.add(key)
            L.need(obs['frame'] == hit['frame'], 'One accumulator frame')
            L.need(obs['cut'] <= hit['cut'] if side == 0 else obs['cut'] >= hit['cut'], 'Causal observation clock')
            q = Q(obs['coefficient'])
            L.need(q != 0, 'Nonzero observation coefficient')
            L.add(total, snapshots[side][key], q)
        want = {int(k): Q(q) for k, q in hit[target].items()}
        L.need(total == want, 'Every timed source coefficient for '+target)
        result[target] = {str(k): str(v) for k, v in sorted(total.items())}
    c, d = ({int(k): Q(q) for k, q in hit[s].items()} for s in ('c', 'd'))
    L.need(sum(q*d.get(r, 0) for r, q in c.items()) == 1, 'Unit boundary pairing')
    return dict(status='PASS_EXACT_TIMED_OBSERVATIONS', gather_count=len(hit['gathers']),
                injection_count=len(hit['injections']), latest_gather=max(x['cut'] for x in hit['gathers']),
                retirement_cut=hit['cut'], earliest_injection=min(x['cut'] for x in hit['injections']),
                vectors=result, boundary_pairing='1')


def controls(word, hit, paths, snapshots=None):
    snapshots = observe(word, hit) if snapshots is None else snapshots
    check(hit, snapshots)
    def rejected(action):
        try:
            action()
        except (ValueError, AssertionError):
            return True
        raise ValueError('Temporal corruption control accepted')
    result = {}
    for field in ('gathers', 'injections'):
        bad = deepcopy(hit)
        bad[field][0]['coefficient'] = str(2*Q(bad[field][0]['coefficient']))
        result['wrong_'+field+'_coefficient'] = rejected(lambda: check(bad, snapshots))
        bad = deepcopy(hit)
        bad[field].pop(0)
        result['omitted_'+field+'_observation'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['cut'] = max(x['cut'] for x in bad['gathers'])-1
    result['retirement_before_last_gather'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['injections'][0]['cut'] = hit['cut']-1
    result['injection_before_retirement'] = rejected(lambda: check(bad, snapshots))
    bad = deepcopy(hit)
    bad['paid_delta'] = {}
    result['omitted_paid_midpoint_cost'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['path']['hi'] = bad['path']['moves'][0]
    result['incomplete_paid_path'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['ranks'] = list(reversed(bad['ranks']))
    result['wrong_productive_ranks'] = rejected(lambda: construct(word, bad, paths))
    bad = deepcopy(hit)
    bad['gathers'][0]['cut'] = hit['cut']+1
    result['gather_after_retirement'] = rejected(lambda: construct(word, bad, paths))
    return result
