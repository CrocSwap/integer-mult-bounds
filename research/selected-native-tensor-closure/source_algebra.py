#!/usr/bin/env python3
"""Complete current-word gauge, ownership and free-Laurent certificates."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib

from gauss_trace import require
from native_check import canonical, span


def add_scaled(dst, src, factor):
    for key, value in tuple(src.items()):
        updated = dst.get(key, 0)+factor*value
        if updated:
            dst[key] = updated
        else:
            dst.pop(key, None)


def local_gauge(word: dict, source_result: dict) -> dict:
    public, owned = word['public'], word['owned_fields']
    require((public, owned) == (770, 29), 'selected public/owned counts')
    total = public+owned
    require(len(word['initial']) == len(word['final']) == public, 'complete local boundaries')
    spaces = [span(vectors) for vectors in word['frames']]
    rows = [{i: Fraction(1)} for i in range(total)]
    current = word['initial'][:]+[None]*owned
    live_owned = set()
    paid = Counter()
    counts = Counter()
    peak = lifetimes = 0
    for index, event in enumerate(word['program']):
        kind, target = event[:2]
        require(type(target) is int and 0 <= target < total, 'local target range')
        counts[kind] += 1
        if kind == 'MOVE':
            require(len(event) == 5, 'MOVE grammar')
            _, _, old, new, private = event
            require(type(private) is bool and current[target] == old and (target in live_owned) == private,
                    f'current native source and ownership at {index}')
            require(spaces[new] < spaces[old] if private else spaces[old] < spaces[new], 'proper nested MOVE')
            paid[abs(len(word['frames'][new])-len(word['frames'][old]))] += 1
            current[target] = new
        elif kind == 'INIT':
            require(len(event) == 3 and target >= public and target not in live_owned, 'fresh owned INIT')
            live_owned.add(target)
            rows[target] = {}
            current[target] = event[2]
            peak = max(peak, len(live_owned))
            lifetimes += 1
        elif kind == 'CLEAR':
            require(len(event) == 3 and target in live_owned and current[target] == event[2], 'owned CLEAR at current chart')
            live_owned.remove(target)
            rows[target] = {}
            current[target] = None
        else:
            require(kind in ('ADD', 'SCALE', 'COPY') and len(event) == (4 if kind == 'SCALE' else 5), 'scalar grammar')
            coefficient, chart = Fraction(event[-2]), event[-1]
            require(coefficient != 0 and current[target] == chart, 'scalar current chart')
            require(coefficient.denominator & (coefficient.denominator-1) == 0, 'dyadic exterior coefficient')
            if kind == 'SCALE':
                rows[target] = {origin: coefficient*value for origin, value in rows[target].items()}
            else:
                source = event[2]
                require(type(source) is int and 0 <= source < total and source != target and current[source] == chart,
                        'exact common-chart source')
                if kind == 'COPY':
                    require(target in live_owned and rows[target] == {}, 'COPY into reached owned zero')
                    rows[target] = {origin: coefficient*value for origin, value in rows[source].items()}
                else:
                    add_scaled(rows[target], rows[source], coefficient)
    require(not live_owned and current[:public] == word['final'] and current[public:] == [None]*owned,
            'all current charts and ownership returned')
    for target, row in enumerate(rows):
        expected = {target: Fraction(1)} if target < public else {}
        if target-112 in word['live']:
            expected[target-112] = Fraction(1)
        require(row == expected, f'complete symbolic gauge endpoint {target}')
    expected = source_result['local']
    require({int(k): v for k, v in expected['paid'].items()} == dict(paid), 'selected paid occurrences')
    require((peak, lifetimes) == (expected['peak_owned_fields'], expected['owned_lifetimes']), 'actual owned chronology')
    encoded = [[[origin, str(coefficient)] for origin, coefficient in sorted(row.items())] for row in rows]
    return {'events': len(word['program']), 'opcode_counts': dict(sorted(counts.items())), 'rows': total,
            'arbitrary_public_columns': public, 'owned_entrance_columns_erased': owned,
            'full_endpoint_coefficients': total*total, 'owned_lifetimes': lifetimes, 'peak_owned': peak,
            'paid_profile': dict(sorted(paid.items())), 'gauge_endpoint_sha256': hashlib.sha256(canonical(encoded)).hexdigest(),
            'rule': 'chart coefficients are formal inverse/forward products; every scalar remains exterior'}


ZERO = (0,)*34


def shift(poly, exponent, factor=1):
    require(len(exponent) == 34, 'all Laurent variables present')
    return {tuple(a+b for a, b in zip(term, exponent, strict=True)): factor*value
            for term, value in poly.items() if factor*value}


def event_pullback(weights, event):
    """Substitute the actual forward assignment into a final linear form."""
    kind = event[0]
    if kind in ('LOCAL', 'QUERY_SHEAR'):
        _, stage, pair, backward = event
        require(type(backward) is bool, 'literal controller orientation')
        x, y = 2*pair, 2*pair+1
        if backward:
            x, y = y, x
        d = ((0,)+tuple(int(j == stage) for j in range(33))) if kind == 'LOCAL' else ZERO
        cross = (1 if backward else -1,)+(0,)*33
        wx, wy = shift(weights[x], d), shift(weights[y], d)
        add_scaled(wx, shift(wy, cross), -1 if backward else 1)
        weights[x], weights[y] = wx, wy
    elif kind == 'IDLE':
        require(len(set(event[2])) == len(event[2]), 'no repeated idle stage')
        d = (0,)+tuple(int(j in event[2]) for j in range(33))
        for row in (2*event[1], 2*event[1]+1):
            weights[row] = shift(weights[row], d)
    elif kind == 'Q_POWER':
        require(event[2] in (-2, 2), 'ordinary even central power')
        weights[event[1]] = shift(weights[event[1]], (event[2],)+(0,)*33)
    elif kind == 'ADD':
        add_scaled(weights[event[2]], weights[event[1]], Fraction(event[3]))
    elif kind == 'SCALE':
        weights[event[1]] = shift(weights[event[1]], ZERO, Fraction(event[2]))
    elif kind == 'SWAP':
        weights[event[1]], weights[event[2]] = weights[event[2]], weights[event[1]]
    else:
        require(kind == 'SIGNED_SWAP', 'controller gate vocabulary')
        weights[event[1]], weights[event[2]] = shift(weights[event[2]], ZERO, -1), weights[event[1]]


def free_laurent(controller: dict) -> dict:
    require((controller['kind'], controller['pairs'], controller['ambient_rank']) == ('complex', 16, 145), 'selected controller type')
    for side in ('left', 'right'):
        for output in range(32):
            weights = [{ZERO: Fraction(int(row == output))} if row == output else {} for row in range(32)]
            for event in reversed(controller['boundaries'][side+'_program']):
                event_pullback(weights, event)
            expected = [{ZERO: Fraction(c)} if Fraction(c) else {} for c in controller['boundaries'][side][output]]
            require(weights == expected, 'literal '+side+' boundary matrix')
    program = controller['boundaries']['right_program']+controller['physical_events']+controller['boundaries']['left_program']
    outputs = []
    for output in range(32):
        weights = [{ZERO: Fraction(1)} if row == output else {} for row in range(32)]
        for event in reversed(program):
            event_pullback(weights, event)
        expected = [{tuple(controller['diagonal'][output]): Fraction(1)} if row == output else {} for row in range(32)]
        require(weights == expected, f'full free-Laurent reverse output {output}')
        outputs.append([output, controller['diagonal'][output], '1'])
    sites = []
    local_count = query_count = 0
    for i, event in enumerate(controller['physical_events']):
        if event[0] == 'QUERY_SHEAR':
            query_count += 1
        if event[0] != 'LOCAL':
            continue
        _, stage, pair, backward = event
        require(not backward, 'all actual suppliers forward')
        local_count += 1
        if stage in controller['wrapper_sites']:
            x, y = 2*pair, 2*pair+1
            require(controller['physical_events'][i-2:i+3] == [
                ['Q_POWER', x, -2], ['SIGNED_SWAP', x, y], event,
                ['Q_POWER', y, 2], ['SIGNED_SWAP', y, x]], 'literal five-step reverse interface')
            sites.append(stage)
    require(sites == controller['wrapper_sites'] and len(sites) == 16 and local_count == 18 and query_count == 15,
            'complete all-forward sites and thin calls')
    return {'controller_events': len(controller['physical_events']), 'literal_boundary_events': len(program)-len(controller['physical_events']),
            'all_1024_laurent_entries_checked': True, 'forward_local_calls': local_count, 'thin_queries_per_port': query_count,
            'five_step_forward_wrappers': len(sites), 'endpoint_sha256': hashlib.sha256(canonical(outputs)).hexdigest(),
            'method': 'reverse linear-functional substitution; no finite-order quotient of Q'}


def ownership_and_invoice(word: dict, controller: dict, source_result: dict) -> dict:
    main_roles = set(word['live']) | {r+112 for r in word['live']}
    helpers = [r for r in range(word['public']) if r not in main_roles]
    calls = [e for e in controller['physical_events'] if e[0] == 'LOCAL']
    mains = 32*len(word['live'])
    productives = mains+len(calls)*len(helpers)
    maps = []
    for call, event in enumerate(calls):
        pair = event[2]
        mapping = {r: (2*pair)*len(word['live'])+j for j, r in enumerate(word['live'])}
        mapping.update({r+112: (2*pair+1)*len(word['live'])+j for j, r in enumerate(word['live'])})
        mapping.update({r: mains+call*len(helpers)+j for j, r in enumerate(helpers)})
        require(set(mapping) == set(range(word['public'])) and len(set(mapping.values())) == word['public'],
                'actual distinct local public owners')
        mapping.update({r: productives+r-word['public'] for r in range(word['public'], word['public']+word['owned_fields'])})
        require(len(set(mapping.values())) == word['public']+word['owned_fields'], 'owned bank disjoint from all public inputs')
        maps.append([mapping[r] for r in range(word['public']+word['owned_fields'])])
    paid = Counter({int(k): len(calls)*v for k, v in source_result['local']['paid'].items()})
    targets = Counter({int(k): len(calls)*v for k, v in source_result['local']['helpers'].items()})
    for event in controller['physical_events']:
        if event[0] == 'QUERY_SHEAR':
            paid[1] += len(word['ports'])
        elif event[0] == 'IDLE':
            paid[8*len(event[2])] += 2*len(word['ports'])
    for diagonal in controller['diagonal']:
        targets[1+8*sum(diagonal[1:])] += len(word['ports'])
    cost = source_result['complete_cost']
    require(dict(paid) == {int(k): v for k, v in cost['paid'].items()}, 'complete paid profile unchanged')
    require(dict(targets) == {int(k): v for k, v in cost['targets'].items()}, 'complete productive profile unchanged')
    require(sum(targets.values()) == productives == 13444, 'all productive owners')
    return {'main_arbitrary_inputs': mains, 'fresh_helper_inputs': len(calls)*len(helpers), 'productive_inputs': productives,
            'local_owned_labels': word['owned_fields'], 'separate_thin_owned_label': productives+word['owned_fields'],
            'paid_calls': sum(paid.values()), 'paid_rank_mass': sum(r*n for r, n in paid.items()),
            'target_rank_mass': sum(r*n for r, n in targets.items()), 'field_maps_sha256': hashlib.sha256(canonical(maps)).hexdigest(),
            'limits': 'ideal source ownership only; allocation, physical erasure and retained backing remain premises'}
