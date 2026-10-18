#!/usr/bin/env python3
"""Exact P104 late-acquisition replay, no producer imports.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The common-chart and private-copy contracts are inherited from PR1972/1991;
the retained correction groups and dirty compensation are from PR2445/2460.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / 'p104-native-channel' / 'inputs'
PINS = {
    'LOWRANK-WITNESS.json': '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
    'P104-FIXTURE.json': '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4',
    'PR2460-CIRCUIT.json': 'ce1b033ae8b826eec87d70246a13a6034e177ef4863bf7f7c24631c79e5202c9',
}
ANTICHAIN = [1, 3, 8, 11, 16, 19, 25, 28, 97, 99]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[path.name], 'source pin: ' + path.name)
    return json.loads(raw)


@lru_cache(maxsize=None)
def _space(vectors):
    result = {0}
    for v in vectors:
        need(type(v) is int and 0 < v < 512 and v not in result, 'independent binary basis')
        result |= {x ^ v for x in tuple(result)}
    return frozenset(result)


def space(vectors):
    return _space(tuple(vectors))


def geometry(fixture):
    roots = {tuple(2 if k == i else 2*sgn if k == j else 0 for k in range(8))
             for i, j in combinations(range(8), 2) for sgn in (-1, 1)}
    roots |= {(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0}
    p = fixture['section4_explicit_P104']
    deleted = set(map(tuple, p['F0'] + p['C']))
    need(len(roots) == 120 and len(deleted) == 16 and deleted <= roots, 'P104 root geometry')
    ports = sorted(roots - deleted)
    half = [[Q(sum(x*y for x, y in zip(a, b)), 8) for b in ports] for a in ports]
    correction = [[Q(t == s)-half[t][s] for s in range(104)] for t in range(3)]
    supports = [{s for s, q in enumerate(row) if q} for row in correction]
    need([len(s) for s in supports] == [48, 48, 48], 'correction support sizes')
    exclusive = sorted(supports[2] - supports[0] - supports[1])
    need(exclusive == [0, 1, 3, 6, 8, 11, 16, 19, 25, 28, 97, 99], 'exclusive sources')
    return half, correction, exclusive


def contacts(word, sources):
    """All inclusive ORIGINAL cut intervals with Xs inside final H2."""
    end, nodes = space(word['final_frames']['Y2']), []
    need(len(end) == 256, 'H2 dimension')
    for s in sources:
        name, start = f'X{s}', 0
        current = word['initial_frames'][name]
        for i, e in enumerate(word['program']):
            if e[:2] == ['transport', name]:
                need(space(current) == space(e[2]) and space(current) < space(e[3]), 'monotone X path')
                if space(current) <= end:
                    nodes.append({'source': s, 'first_cut': start, 'last_cut': i, 'frame': current})
                current, start = e[3], i+1
            if e[0] in ('add', 'copy'):
                need(e[1] != name, 'immutable X input')
        if space(current) <= end:
            nodes.append({'source': s, 'first_cut': start, 'last_cut': len(word['program']), 'frame': current})
    return nodes


def path_cover(nodes, sources):
    """Earliest finish dominates later finishes at the same last contact."""
    indices = {s: i for i, s in enumerate(sources)}
    spaces = [space(n['frame']) for n in nodes]
    size = 1 << len(sources)
    dp = [{} for _ in range(size)]
    for i, n in enumerate(nodes):
        dp[1 << indices[n['source']]][i] = n['first_cut']
    for mask in range(1, size):
        for last, time in tuple(dp[mask].items()):
            for nxt, n in enumerate(nodes):
                bit = 1 << indices[n['source']]
                if mask & bit or not spaces[last] <= spaces[nxt]:
                    continue
                at = max(time, n['first_cut'])
                if at <= n['last_cut'] and at < dp[mask | bit].get(nxt, 10**9):
                    dp[mask | bit][nxt] = at
    best = [len(sources)+1] * size
    best[0] = 0
    for mask in range(1, size):
        bit, sub = mask & -mask, mask
        while sub:
            if sub & bit and dp[sub]:
                best[mask] = min(best[mask], 1 + best[mask ^ sub])
            sub = (sub-1) & mask
    feasible = [m for m in range(1, size) if dp[m]]
    return {'source_sets': size-1, 'contact_intervals': len(nodes),
            'reachable_states': sum(map(len, dp)), 'one_path_masks': feasible,
            'one_path_sizes': dict(sorted(Counter(m.bit_count() for m in feasible).items())),
            'minimum_paths': best[-1]}


def antichain_certificate(nodes):
    result = []
    for a, b in combinations(ANTICHAIN, 2):
        left = [n for n in nodes if n['source'] == a]
        right = [n for n in nodes if n['source'] == b]
        need(left and right, 'antichain coverage')
        witnesses = []
        for x, y in product(left, right):
            A, B = space(x['frame']), space(y['frame'])
            need(A-B and B-A, 'antichain incomparable contacts')
            witnesses.append([x['first_cut'], y['first_cut'], min(A-B), min(B-A)])
        result.append({'sources': [a, b], 'noncontainment_witnesses': witnesses})
    return result


def replay(word, circuit, half):
    new = circuit['initial_frames'] if circuit else {}
    need(not set(new) & set(word['initial_frames']), 'new helper alias')
    initial = {**word['initial_frames'], **new}
    names = sorted(initial)
    fs = {r: space(f) for r, f in initial.items()}
    rows = {r: {r: Q(1)} for r in names}
    need(all(fs[r] == {0} for r in new), 'dirty ZERO entry')
    cuts = {}
    if circuit:
        need(circuit['targets'] == [0, 1, 2], 'target scope')
        for entry in circuit['insertions']:
            cut = entry['completed_cut']
            need(type(cut) is int and 0 <= cut <= len(word['program']) and cut not in cuts, 'insertion cut')
            cuts[cut] = entry['events']
    counts, hist, added = Counter(), Counter(), Counter()
    peak, denom = Q(1), 1

    def execute(e, is_new):
        nonlocal peak, denom
        op, dst = e[:2]
        counts['events'] += 1
        if is_new:
            need(op in ('add', 'transport'), 'added alphabet')
        if op == 'add':
            _, dst, src, q, f = e
            need(src != dst and src in rows and dst in rows, 'ADD register')
            need(fs[src] == fs[dst] == space(f), 'ADD common frame')
            q = Q(q)
            need(q and q.denominator & (q.denominator-1) == 0, 'dyadic ADD')
            if is_new:
                need(dst in new or dst in ('Y0', 'Y1', 'Y2'), 'added destination')
                need(src in new or src.startswith('X'), 'added source')
                need(dst in new or src in new, 'helper target delivery')
                counts['added_adds'] += 1
                counts['source_reads'] += int(src.startswith('X'))
            else:
                need(not src.startswith('Y') and not dst.startswith('X'), 'original data contract')
            for col, v in rows[src].items():
                value = rows[dst].get(col, Q(0)) + q*v
                if value:
                    rows[dst][col] = value
                else:
                    rows[dst].pop(col, None)
        elif op == 'transport':
            _, dst, old, target, price = e
            A, B = space(old), space(target)
            need(dst in rows and fs[dst] == A, 'transport entry frame')
            need(A < B or B < A, 'nested transport')
            need(type(price) is int and price == abs(len(old)-len(target)), 'dimension-gap charge')
            if is_new:
                need(dst in new and A < B, 'added monotonicity')
                added[price] += 1
            else:
                need(A < B or dst == 'C', 'original private descent')
            hist[price] += 1
            fs[dst] = B
        elif op == 'zero':
            need(dst == 'C' and dst not in rows, 'owned allocation')
            rows[dst], fs[dst] = {}, space(e[2])
            counts['private_allocations'] += 1
        elif op == 'copy':
            _, dst, src, f = e
            need(dst == 'C' and dst in rows and not rows[dst] and src in rows, 'owned copy')
            need(fs[dst] == fs[src] == space(f), 'copy frame')
            rows[dst] = dict(rows[src])
            counts['private_copies'] += 1
        elif op == 'erase':
            need(dst == 'C' and dst in rows and fs[dst] == space(e[2]), 'owned discard')
            del rows[dst], fs[dst]
            counts['private_discards'] += 1
            return
        else:
            raise ValueError('unknown operation')
        peak = max(peak, sum(map(abs, rows[dst].values()), Q(0)))
        denom = max(denom, max((q.denominator for q in rows[dst].values()), default=1))

    for cut in range(len(word['program'])+1):
        for e in cuts.get(cut, []):
            execute(e, True)
        if cut < len(word['program']):
            execute(word['program'][cut], False)
    exits = {**word['final_frames'], **(circuit['final_frames'] if circuit else {})}
    need(set(rows) == set(exits) == set(names), 'final register coverage')
    for r in names:
        expected = {r: Q(1)}
        if r.startswith('Y'):
            t = int(r[1:])
            coeff = [Q(t == s) for s in range(104)] if circuit and t < 3 else half[t]
            expected.update({f'X{s}': q for s, q in enumerate(coeff) if q})
        need(rows[r] == expected, 'endpoint: ' + r)
        need(fs[r] == space(exits[r]), 'final frame: ' + r)
        if r in new:
            need(len(fs[r]) == 512, 'dirty FULL exit')
    need(all(counts[k] == 8 for k in ('private_allocations', 'private_copies', 'private_discards')), 'private lifetimes')
    payload = [[r, [[c, str(q)] for c, q in sorted(rows[r].items())]] for r in names]
    return {**dict(sorted(counts.items())), 'helper_lifetimes': len(new), 'input_columns': len(names),
            'endpoint_coefficients': len(names)**2, 'added_profile': dict(sorted(added.items())),
            'full_profile': dict(sorted(hist.items())), 'added_transports': sum(added.values()),
            'added_rank_mass': sum(k*v for k, v in added.items()), 'full_rank_mass': sum(k*v for k, v in hist.items()),
            'logical_prefix_l1': str(peak), 'maximum_logical_denominator': denom,
            'endpoint_sha256': sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()}


def retained_stream(circuit, removed):
    return [[ins['completed_cut'], e] for ins in circuit['insertions'] for e in ins['events']
            if e[1] not in removed and not (e[0] == 'add' and e[2] in removed)]


def validate_delta(word, ancestor, candidate, correction, sources, nodes):
    old = {f'N{s}' for s in sources}
    info = candidate['late_acquisition']
    need(info['target'] == 2 and info['sources'] == sources and info['mode'] == 'late', 'mechanism metadata')
    helpers = {r['helper'] for r in info['routes']}
    need(len(helpers) == len(info['routes']) == 10, 'ten distinct path helpers')
    need(candidate['groups'] == [g for g in ancestor['groups'] if g['targets'] != [2]], 'six retained groups')
    for field in ('initial_frames', 'final_frames'):
        need({r: f for r, f in candidate[field].items() if r not in helpers} ==
             {r: f for r, f in ancestor[field].items() if r not in old}, 'retained helper boundaries')
    need(retained_stream(ancestor, old) == retained_stream(candidate, helpers), 'retained insertion stream')
    actual, declared, captured = Counter(), Counter(), []
    for route in info['routes']:
        helper, prior_cut, prior_frame = route['helper'], 0, frozenset({0})
        for capture in route['captures']:
            s, cut, F, q = capture['source'], capture['cut'], space(capture['frame']), Q(capture['coefficient'])
            need(s in sources and cut >= prior_cut and prior_frame <= F, 'route chronology')
            need(any(n['source'] == s and n['first_cut'] <= cut <= n['last_cut'] and space(n['frame']) == F
                     for n in nodes), 'source contact interval')
            need(q == correction[2][s], 'capture coefficient')
            declared[(cut, helper, f'X{s}', str(q))] += 1
            declared[(len(word['program']), helper, f'X{s}', str(-q))] += 1
            captured.append(s)
            prior_cut, prior_frame = cut, F
    need(sorted(captured) == sources, 'exclusive source coverage')
    deliveries, compensations = Counter(), Counter()
    for ins in candidate['insertions']:
        cut = ins['completed_cut']
        for e in ins['events']:
            if e[0] != 'add':
                continue
            _, dst, src, q, f = e
            if dst in helpers:
                need(src.startswith('X'), 'isolated path source')
                actual[(cut, dst, src, str(Q(q)))] += 1
            if src in helpers:
                need(dst == 'Y2', 'exclusive destination')
                if cut == 0 and space(f) == {0} and Q(q) == -1:
                    compensations[src] += 1
                elif cut == len(word['program']) and space(f) == space(word['final_frames']['Y2']) and Q(q) == 1:
                    deliveries[src] += 1
                else:
                    raise ValueError('dirty compensation/delivery')
    need(actual == declared, 'literal route binding')
    need(deliveries == compensations == Counter({r: 1 for r in helpers}), 'one cancellation per path')


def initial_line_control(word, ancestor, sources, correction):
    """Independent-entry comparator, without the predecessor's optional gather."""
    old = {f'N{s}' for s in sources}
    c = {'targets': [0, 1, 2], 'initial_frames': {}, 'final_frames': {}, 'insertions': []}
    for field in ('initial_frames', 'final_frames'):
        c[field] = {r: f for r, f in ancestor[field].items() if r not in old}
    before, after = [], []
    for cut, e in retained_stream(ancestor, old):
        (before if cut == 0 else after).append(e)
    full, end = [1 << i for i in range(9)], word['final_frames']['Y2']
    for s in sources:
        r, line, q = f'CONTROL{s}', word['initial_frames'][f'X{s}'], correction[2][s]
        c['initial_frames'][r], c['final_frames'][r] = [], full
        before.extend([['add', 'Y2', r, '-1', []], ['transport', r, [], line, 1], ['add', r, f'X{s}', str(q), line]])
        after.extend([['transport', r, line, end, 7], ['add', 'Y2', r, '1', end],
                      ['transport', r, end, full, 1], ['add', r, f'X{s}', str(-q), full]])
    c['insertions'] = [{'completed_cut': 0, 'events': before}, {'completed_cut': len(word['program']), 'events': after}]
    return c


def controls(word, candidate, half, nodes, sources):
    rejected = []

    def reject(name, mutate, reason):
        c = deepcopy(candidate)
        mutate(c)
        try:
            replay(word, c, half)
        except ValueError as error:
            need(reason in str(error), name + ' wrong failure: ' + str(error))
            rejected.append(name)
        else:
            raise ValueError('accepted fault: ' + name)

    def edit(c, dst, src, cut, change):
        for ins in c['insertions']:
            if ins['completed_cut'] == cut:
                for i, e in enumerate(ins['events']):
                    if e[:3] == ['add', dst, src]:
                        change(ins['events'], i)
                        return
        raise ValueError('fault target not found')

    end = len(word['program'])
    drop = lambda events, i: events.pop(i)
    for name, dst, src, cut, reason in [
        ('missing_dirty_compensation', 'Y2', 'LATE0', 0, 'endpoint: Y2'),
        ('missing_late_X1', 'LATE0', 'X1', 669, 'endpoint: LATE0'),
        ('missing_FULL_cleanup', 'LATE0', 'X1', end, 'endpoint: LATE0'),
        ('missing_delivery', 'Y2', 'LATE0', end, 'endpoint: Y2')]:
        reject(name, lambda c, d=dst, s=src, k=cut: edit(c, d, s, k, drop), reason)
    reject('wrong_late_X0_sign', lambda c: edit(c, 'LATE0', 'X0', 842,
           lambda es, i: es[i].__setitem__(3, str(-Q(es[i][3])))), 'endpoint: LATE0')
    def shift(c, old, new):
        next(ins for ins in c['insertions'] if ins['completed_cut'] == old)['completed_cut'] = new
    reject('X1_one_cut_early', lambda c: shift(c, 669, 668), 'ADD common frame')
    reject('X0_after_escape', lambda c: shift(c, 842, 1076), 'ADD common frame')
    def undercharge(c):
        next(e for ins in c['insertions'] for e in ins['events'] if e[:2] == ['transport', 'LATE0'])[4] -= 1
    reject('undercharged_transport', undercharge, 'dimension-gap charge')
    reject('nonFULL_dirty_exit', lambda c: c['final_frames'].__setitem__('LATE0', []), 'final frame')
    bad_nodes = deepcopy(nodes)
    next(n for n in bad_nodes if n['source'] == 3)['frame'] = next(n for n in bad_nodes if n['source'] == 1)['frame']
    try:
        antichain_certificate(bad_nodes)
    except ValueError as error:
        need('incomparable' in str(error), 'antichain control')
        rejected.append('comparable_antichain_contacts')
    else:
        raise ValueError('accepted antichain fault')
    need(path_cover([n for n in nodes if n['first_cut'] == 0], sources)['minimum_paths'] == 12, 'initial-line floor')
    c = deepcopy(candidate)
    for field in ('initial_frames', 'final_frames'):
        for f in c[field].values():
            f.reverse()
    for ins in c['insertions']:
        for e in ins['events']:
            for pos in ([2, 3] if e[0] == 'transport' else [4]):
                # JSON may share list objects in memory; assign rather than mutate.
                e[pos] = list(reversed(e[pos]))
    need(replay(word, c, half) == replay(word, candidate, half), 'equivalent frame bases')
    return {'rejected': rejected, 'positive': ['initial_line_floor_12', 'equivalent_binary_bases']}


def run():
    word = pinned(NATIVE / 'LOWRANK-WITNESS.json')
    fixture = pinned(NATIVE / 'P104-FIXTURE.json')
    ancestor = pinned(HERE / 'inputs' / 'PR2460-CIRCUIT.json')
    candidate = json.loads((HERE / 'CIRCUIT.json').read_text())
    half, correction, sources = geometry(fixture)
    nodes = contacts(word, sources)
    cover = path_cover(nodes, sources)
    need(cover['minimum_paths'] == 10, 'path-cover optimum')
    validate_delta(word, ancestor, candidate, correction, sources, nodes)
    late = sorted({n['source'] for n in contacts(word, range(104)) if n['first_cut'] > 0 and correction[2][n['source']]})
    return {'schema_version': 1, 'base_commit': '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
            'assignment_seed': 34, 'source_pins': PINS, 'exclusive_Y2_sources': sources,
            'later_compatible_Y2_sources': late, 'exclusive_with_later_access': sorted(set(late) & set(sources)),
            'contacts': nodes, 'path_search': cover, 'antichain_sources': ANTICHAIN,
            'antichain_certificate': antichain_certificate(nodes),
            'original_channel': replay(word, None, half), 'PR2460_literal': replay(word, ancestor, half),
            'initial_line_direct_control': replay(word, initial_line_control(word, ancestor, sources, correction), half),
            'candidate': replay(word, candidate, half), 'controls': controls(word, candidate, half, nodes, sources),
            'scope': 'Finite three-target logical construction; sharp ten-lifetime floor only for the isolated twelve-source X-only monotone correction. No new kappa or native/global supplier admission.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--regenerate', action='store_true')
    p.add_argument('--out-result', type=Path, help='authoring: write a NEW receipt instead of checking RESULT.json')
    args = p.parse_args()
    result = json.loads(json.dumps(run()))
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-late-s34-') as tmp:
            out = Path(tmp) / 'circuit.json'
            subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'build.py'), '--out', str(out)], check=True)
            need(json.loads(out.read_text()) == json.loads((HERE / 'CIRCUIT.json').read_text()), 'complete regenerated circuit')
    if args.out_result:
        with args.out_result.open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == result, 'complete receipt equality')
    c = result['candidate']
    print(f"PASS_P104_LATE_Y2_S34 paths=10 helpers={c['helper_lifetimes']} adds={c['added_adds']} "
          f"rank_mass={c['added_rank_mass']} endpoint_coefficients={c['endpoint_coefficients']} "
          f"rejecting_controls={len(result['controls']['rejected'])} no_new_kappa")


if __name__ == '__main__':
    main()
