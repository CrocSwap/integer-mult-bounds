"""Forward source Laurent prefixes and exact caller ownership/debt reset."""
from collections import Counter
from fractions import Fraction
import hashlib

from common import digest, encoded, integer, require, row_record

ZERO = (0,)*34


def shifted(row, shifts=(), coefficient=1):
    out = {}
    for (origin, powers), value in row.items():
        new = list(powers)
        for index, power in shifts:
            new[index] += power
        if coefficient*value:
            out[origin, tuple(new)] = coefficient*value
    return out


def combined(left, right, coefficient=1):
    out = dict(left)
    for key, value in right.items():
        total = out.get(key, 0)+coefficient*value
        if total:
            out[key] = total
        else:
            out.pop(key, None)
    return out


def step(rows, event):
    require(type(event) is list and event, 'literal controller event')
    kind = event[0]
    if kind in ('LOCAL', 'QUERY_SHEAR'):
        require(len(event) == 4 and type(event[3]) is bool, 'local/query grammar')
        stage = integer(event[1], 0, 32, 'stage')
        pair = integer(event[2], 0, 15, 'pair')
        x, y = 2*pair, 2*pair+1
        if event[3]:
            rows[x] = combined(rows[x], shifted(rows[y], [(0, 1)]), -1)
        else:
            rows[y] = combined(rows[y], shifted(rows[x], [(0, -1)]))
        if kind == 'LOCAL':
            rows[x] = shifted(rows[x], [(stage+1, 1)])
            rows[y] = shifted(rows[y], [(stage+1, 1)])
    elif kind == 'IDLE':
        require(len(event) == 3 and type(event[2]) is list and len(set(event[2])) == len(event[2]), 'idle grammar')
        pair = integer(event[1], 0, 15, 'idle pair')
        shifts = [(integer(s, 0, 32, 'idle stage')+1, 1) for s in event[2]]
        for target in (2*pair, 2*pair+1):
            rows[target] = shifted(rows[target], shifts)
    elif kind == 'Q_POWER':
        require(len(event) == 3 and type(event[2]) is int and event[2] in (-2, 2), 'Q square grammar')
        target = integer(event[1], 0, 31, 'Q target')
        rows[target] = shifted(rows[target], [(0, event[2])])
    elif kind in ('ADD', 'SCALE'):
        require(len(event) == (4 if kind == 'ADD' else 3), 'controller scalar arity')
        target = integer(event[1], 0, 31, 'controller scalar target')
        require(type(event[-1]) in (str, int), 'controller scalar literal')
        coefficient = Fraction(event[-1])
        require(coefficient.denominator == 1 and abs(coefficient) == 1, 'integral signed controller scalar')
        if kind == 'ADD':
            source = integer(event[2], 0, 31, 'controller scalar source')
            require(source != target, 'controller distinct ADD')
            rows[target] = combined(rows[target], rows[source], int(coefficient))
        else:
            rows[target] = shifted(rows[target], coefficient=int(coefficient))
    elif kind in ('SWAP', 'SIGNED_SWAP'):
        require(len(event) == 3, 'exchange arity')
        x = integer(event[1], 0, 31, 'exchange X')
        y = integer(event[2], 0, 31, 'exchange Y')
        require(x != y, 'exchange distinct roles')
        rows[x], rows[y] = rows[y], shifted(rows[x], coefficient=-1 if kind == 'SIGNED_SWAP' else 1)
    else:
        raise ValueError('unknown controller opcode')


def replay(events):
    rows = [{(i, ZERO): 1} for i in range(32)]
    cuts = hashlib.sha256()
    maximum = 1
    witness = [0, 0]
    peak_terms = 32
    entrance = []
    for index in range(len(events)+1):
        for role, row in enumerate(rows):
            require(all(type(c) is int for c in row.values()), 'integral Laurent prefix')
            total = sum(map(abs, row.values()))
            if total > maximum:
                maximum, witness = total, [index, role]
        peak_terms = max(peak_terms, sum(map(len, rows)))
        cuts.update(encoded([index, [row_record(r) for r in rows]]))
        if index < len(events):
            event = events[index]
            if event[0] == 'LOCAL':
                x = 2*event[2]
                entrance.append([index, event[1], event[2], sum(map(abs, rows[x].values())),
                                 sum(map(abs, rows[x+1].values()))])
            step(rows, event)
    return rows, {'cuts': len(events)+1, 'maximum_mass': maximum, 'first_mass_witness': witness,
                  'peak_terms': peak_terms, 'complete_cut_sha256': cuts.hexdigest(), 'local_entrances': entrance}


def certify(word, controller, source_result, dependency):
    require(controller['kind'] == 'complex' and controller['pairs'] == 16
            and controller['ambient_rank'] == 145, 'selected complete controller')
    for side in ('right', 'left'):
        actual, _ = replay(controller['boundaries'][side+'_program'])
        expected = [{(j, ZERO): Fraction(v) for j, v in enumerate(row) if Fraction(v)}
                    for row in controller['boundaries'][side]]
        require(actual == expected, 'complete literal boundary '+side)
    physical = controller['physical_events']
    events = controller['boundaries']['right_program']+physical+controller['boundaries']['left_program']
    rows, result = replay(events)
    expected = [{(i, tuple(exponents)): 1} for i, exponents in enumerate(controller['diagonal'])]
    require(rows == expected and len(events) == 363 and result['maximum_mass'] <= 10, 'complete free-Laurent endpoint/range')
    local = [e for e in physical if e[0] == 'LOCAL']
    require(len(local) == 18 and all(e[3] is False for e in local), 'all18 source invocations forward')
    wrapped = []
    for i, event in enumerate(physical):
        if event[0] != 'LOCAL' or event[1] not in controller['wrapper_sites']:
            continue
        x, y = 2*event[2], 2*event[2]+1
        require(physical[i-2:i+3] == [['Q_POWER', x, -2], ['SIGNED_SWAP', x, y], event,
                                   ['Q_POWER', y, 2], ['SIGNED_SWAP', y, x]], 'complete reverse wrapper cuts')
        wrapped.append(event[1])
    require(wrapped == controller['wrapper_sites'] and len(wrapped) == 16, 'all16 reverse interfaces')
    main = set(word['live']) | {r+112 for r in word['live']}
    helpers = [r for r in range(word['public']) if r not in main]
    require(len(helpers) == 562, 'arbitrary helper count')
    maps = []
    for call, event in enumerate(local):
        mapping = {r: 208*event[2]+j for j, r in enumerate(word['live'])}
        mapping.update({r+112: 208*event[2]+104+j for j, r in enumerate(word['live'])})
        mapping.update({r: 3328+562*call+j for j, r in enumerate(helpers)})
        require(len(set(mapping.values())) == 770, 'distinct public source owners')
        mapping.update({r: 13444+r-770 for r in range(770, 799)})
        require(set(mapping) == set(range(799)) and len(set(mapping.values())) == 799, 'disjoint owned bank')
        maps.append([mapping[r] for r in range(799)])
    require(digest(maps) == dependency['ownership_and_invoice']['field_maps_sha256'], 'same actual A1 owners')
    counts = Counter(e[0] for e in physical)
    paid = Counter({int(k): 18*v for k, v in source_result['local']['paid'].items()})
    paid[1] += 104*counts['QUERY_SHEAR']
    for event in physical:
        if event[0] == 'IDLE':
            paid[8*len(event[2])] += 208
    require(dict(paid) == {int(k): v for k, v in source_result['complete_cost']['paid'].items()}, 'unchanged complete paid profile')
    result.update({'events': len(events), 'all_prefix_coefficients_integral': True,
                   'local_calls': 18, 'reverse_interfaces': 16, 'thin_queries': 104*counts['QUERY_SHEAR'],
                   'thin_scratch_label': 13473, 'productive_fields': 13444,
                   'paid_calls': sum(paid.values()), 'paid_rank_mass': sum(r*v for r, v in paid.items()),
                   'field_maps_sha256': digest(maps),
                   'paid_profile': {str(k): v for k, v in sorted(paid.items())}})
    return result
