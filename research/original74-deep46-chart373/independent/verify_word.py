#!/usr/bin/env python3
"""Independent literal and invoice replay of the frozen original-74 word."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path


SECONDARY_SHA = '6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
BASE_SHA = '450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66'
PRIMARY = (41078, 41079, 41080, 41171, 42116)
EXPECTED_EDITS = {
    41078: (['MOVE', 134, 3, 618, False], ['MOVE', 134, 3, 373, False]),
    41079: (['MOVE', 329, 373, 618, False], None),
    41080: (['ADD', 134, 329, '-1/2', 618], ['ADD', 134, 329, '-1/2', 373]),
    41171: (['MOVE', 329, 618, 733, False], ['MOVE', 329, 373, 733, False]),
    42116: (['MOVE', 134, 618, 913, False], ['MOVE', 134, 373, 913, False]),
}
ROLE_EXITS = {134: 42116, 329: 41171}
FIRST_READS = {134: 43856, 329: 41172}
COURIER = {
    41463: ['MOVE', 990, 260, 719, False],
    41464: ['MOVE', 473, 716, 719, False],
    41465: ['ADD', 990, 473, '-1', 719],
    41466: ['MOVE', 226, 260, 719, False],
    41467: ['ADD', 473, 226, '1', 719],
    41468: ['ADD', 990, 226, '-1', 719],
    41469: ['MOVE', 990, 719, 907, False],
    41470: ['ADD', 990, 931, '1/2', 907],
}
DEEP = 47995
PEER_K = Fraction('.0036524238117')
BASE_K = Fraction('.0036521182092')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as source:
        return json.load(source)


def canonical_sha(value):
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return sha256(encoded).hexdigest()


def difference(after, before):
    return {key: after.get(key, 0) - before.get(key, 0)
            for key in sorted(after.keys() | before.keys())
            if after.get(key, 0) != before.get(key, 0)}


@cache
def rank_power(rank, k):
    """Enclose rank**(1-k) using directed integer operations on a dyadic grid."""
    require(type(rank) is int and rank >= 1, f'invalid rank {rank}')
    require(0 < k < 1, f'invalid k {k}')
    bits = 96
    unit = 1 << bits
    exponent = 1 - k
    digits, tail = divmod(exponent.numerator * unit, exponent.denominator)
    value_lower = value_upper = unit
    root_lower = root_upper = rank * unit
    for shift in reversed(range(bits)):
        root_lower = isqrt(root_lower * unit)
        radicand = root_upper * unit
        root_upper = isqrt(radicand)
        if root_upper ** 2 < radicand:
            root_upper += 1
        if digits & (1 << shift):
            value_lower = value_lower * root_lower // unit
            value_upper = -(-value_upper * root_upper // unit)
    if tail:
        value_upper = -(-value_upper * root_upper // unit)
    return Fraction(value_lower, unit), Fraction(value_upper, unit)


def histogram_bounds(histogram, k):
    lower = upper = Fraction(0)
    for rank, coefficient in histogram.items():
        bounds = rank_power(rank, k)
        ends = [coefficient * bound for bound in bounds]
        lower += min(ends)
        upper += max(ends)
    return lower, upper


def interval_text(interval, places=24):
    scale = 10 ** places
    endpoints = [interval[0] * scale, -(interval[1] * scale)]
    integers = [value.numerator // value.denominator for value in endpoints]
    return [str(Fraction(integers[0], scale)), str(Fraction(-integers[1], scale))]


def invoice_histogram(raw, name):
    result = {}
    for rank, count in raw[name].items():
        require(rank == str(int(rank)) and int(rank) > 0 and
                type(count) is int and count > 0, f'invalid {name} row {rank}: {count}')
        result[int(rank)] = count
    return result


def read_invoice(raw):
    require(type(raw['S']) is int and raw['S'] >= 0, 'invalid rank surplus')
    require(raw['empty_root_credits'] == 0, 'expected no empty-root credits')
    invoice = {'P': invoice_histogram(raw, 'P'), 'S': raw['S'],
               'T': invoice_histogram(raw, 'T')}
    require(invoice['S'] == -rank_mass(signed(invoice)), 'invoice rank surplus mismatch')
    return invoice


def rank_mass(histogram):
    return sum(rank * count for rank, count in histogram.items())


def signed(invoice):
    return difference(invoice['P'], invoice['T'])


def invoice_delta(after, before):
    return {'P': difference(after['P'], before['P']),
            'S': after['S'] - before['S'],
            'T': difference(after['T'], before['T'])}


def pricing_report(base, candidate, peer):
    report = {}
    for name, other, k in (('base7645', base, BASE_K), ('peer7657', peer, PEER_K)):
        delta = difference(signed(candidate), signed(other))
        interval = histogram_bounds(delta, k)
        signed_candidate = histogram_bounds(signed(candidate), k)
        report[name] = {'k': str(k), 'invoice_delta': invoice_delta(candidate, other),
                        'signed_delta': delta, 'difference_interval': interval_text(interval),
                        'candidate_invoice_interval': interval_text(signed_candidate),
                        'candidate_delta_sign': 'lower' if interval[1] < 0 else
                        'higher' if interval[0] > 0 else 'undetermined'}
    return report


def span_mask(vectors):
    span = 1
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512 and not (span >> vector & 1),
                f'dependent chart vector {vector}')
        points = span
        while points:
            bit = points & -points
            span |= 1 << ((bit.bit_length() - 1) ^ vector)
            points ^= bit
    return span


def add_rows(destination, source, multiplier):
    result = destination.copy()
    for column, coefficient in source.items():
        value = result.get(column, 0) + multiplier * coefficient
        if value:
            result[column] = value
        else:
            result.pop(column, None)
    return result


def row_tuple(row):
    return tuple(sorted(row.items()))


def replay(word, tagged, watch=()):
    """Use sparse rational coefficient vectors for arbitrary public inputs."""
    width = word['public']
    owned = word['owned_fields']
    frames = list(word['initial']) + [None] * owned
    dimensions = list(map(len, word['frames']))
    spans = list(map(span_mask, word['frames']))
    require(len(frames) == width + owned, 'initial width mismatch')
    rows = [{wire: Fraction(1)} for wire in range(width)] + [{} for _ in range(owned)]
    active = {}
    erased = {}
    observed = {}
    boundary = {}
    paid = Counter()
    mechanisms = Counter()
    watched = set(watch)

    def check_chart(chart):
        require(type(chart) is int and 0 <= chart < len(spans), f'{clock}: invalid chart {chart}')

    def snapshot(wire):
        return frames[wire], row_tuple(rows[wire]), active.get(wire)

    for clock, event in tagged:
        op, dst, *args = event
        require(type(dst) is int and 0 <= dst < len(rows), f'{clock}: invalid register {dst}')
        src = args[0] if op in ('ADD', 'COPY') else dst
        require(type(src) is int and 0 <= src < len(rows), f'{clock}: invalid source {src}')
        private_event = dst >= width or src >= width
        traced = clock in watched or private_event or op == 'COPY'
        before = (snapshot(dst), snapshot(src)) if traced else None
        if op == 'INIT':
            chart, = args
            check_chart(chart)
            require(dst >= width and frames[dst] is None and dst not in active and not rows[dst],
                    f'{clock}: initialization of occupied register {dst}')
            active[dst] = clock
            frames[dst] = chart
        elif op == 'CLEAR':
            chart, = args
            check_chart(chart)
            require(dst in active and frames[dst] == chart, f'{clock}: invalid owner at erase')
            erased[clock] = (dst, active.pop(dst), chart, row_tuple(rows[dst]))
            rows[dst], frames[dst] = {}, None
        elif op == 'MOVE':
            old, new, private = args
            check_chart(old)
            check_chart(new)
            require(type(private) is bool and private == (dst >= width) and
                    (not private or dst in active) and frames[dst] == old,
                    f'{clock}: invalid MOVE chart or owner on {dst}')
            old_span, new_span = spans[old], spans[new]
            upward = old_span != new_span and old_span & new_span == old_span
            downward = old_span != new_span and old_span & new_span == new_span
            require(upward or (private and downward), f'{clock}: nonnested MOVE {old}->{new}')
            rank = abs(dimensions[new] - dimensions[old])
            paid[rank] += 1
            kind = 'private_rise' if private and upward else 'private_fall' if private else 'public_rise'
            mechanisms[kind, rank] += 1
            frames[dst] = new
        else:
            require(op in ('ADD', 'COPY', 'SCALE'), f'{clock}: unknown opcode {op}')
            coefficient, chart = args[-2:]
            check_chart(chart)
            q = Fraction(coefficient)
            require(len(args) == (2 if op == 'SCALE' else 3) and q and abs(q) + 1 < 2 ** 16 and
                    frames[dst] == frames[src] == chart and ((src == dst) == (op == 'SCALE')),
                    f'{clock}: invalid {op} operands or chart ({dst}, {src}) at {chart}, have '
                    f'({frames[dst]}, {frames[src]})')
            if op == 'COPY':
                require(dst in active and not rows[dst], f'{clock}: COPY destination is occupied')
            destination = {} if op == 'SCALE' else rows[dst]
            rows[dst] = add_rows(destination, rows[src], q)
        if traced:
            observation = (tuple(event), before, (snapshot(dst), snapshot(src)))
            if private_event or op == 'COPY':
                observed[clock] = observation
            if clock in watched:
                boundary[clock] = observation

    require(not active and frames == word['final'] + [None] * owned,
            'final chart or ownership mismatch')
    return {'rows': tuple(map(row_tuple, rows[:width])), 'observed': observed,
            'erased': erased, 'boundary': boundary, 'paid': paid, 'mechanisms': mechanisms}


def align(base, candidate):
    require({key: value for key, value in base.items() if key != 'program'} ==
            {key: value for key, value in candidate.items() if key != 'program'},
            'word metadata changed')
    tagged = []
    candidate_program = iter(candidate['program'])
    for clock, event in enumerate(base['program']):
        if clock in EXPECTED_EDITS:
            old, new = EXPECTED_EDITS[clock]
            require(old == event, f'unexpected base event at {clock}')
        else:
            new = event
        if new is not None:
            actual = next(candidate_program, None)
            require(actual == new, f'out-of-scope candidate event at base clock {clock}')
            tagged.append((clock, actual))
    require(next(candidate_program, None) is None, 'extra candidate events')
    require(base['program'][DEEP] == ['MOVE', 46, 513, 127, False], 'deeper role 46 contact missing')
    require(all(base['program'][clock] == event for clock, event in COURIER.items()),
            'original 226/990 courier does not match its literal anchors')
    return tagged


def relevant_clocks(program):
    events = set(PRIMARY) | set(COURIER) | set(range(DEEP, DEEP + 8))
    for role, exit_clock in ROLE_EXITS.items():
        first_read = next(clock for clock in range(exit_clock + 1, len(program))
                          if program[clock][0] in ('ADD', 'COPY') and program[clock][2] == role)
        require(first_read == FIRST_READS[role], f'first exterior read of {role} moved')
        events.update(clock for clock in range(exit_clock + 1, first_read + 1)
                      if program[clock][1] == role or
                      (program[clock][0] in ('ADD', 'COPY') and program[clock][2] == role))
    return events


def without_chart(observation):
    _, before, after = observation
    return tuple(tuple(value[1:] for value in positions) for positions in (before, after))


def serial_row(row):
    return [[wire, str(coefficient)] for wire, coefficient in row]


def add_observation(observation, label):
    event, before, after = observation
    require(event[0] == 'ADD', f'{label}: ADD required')
    destination, source = map(lambda value: dict(value[1]), before)
    expected = row_tuple(add_rows(destination, source, Fraction(event[3])))
    require(after[0][1] == expected and before[1] == after[1], f'{label}: ADD action')
    return {'event': event, 'destination_before': serial_row(before[0][1]),
            'source': serial_row(before[1][1]), 'destination_after': serial_row(expected)}


def boundary_report(base, candidate, watched):
    expected_contact = set(PRIMARY) - {41079}
    for clock in sorted(watched):
        if clock == 41079:
            continue
        before, after = base['boundary'][clock], candidate['boundary'][clock]
        if clock in expected_contact:
            require(without_chart(before) == without_chart(after), f'changed value at contact {clock}')
        else:
            require(before == after, f'changed exterior read or action at {clock}')
    trace = candidate['boundary']
    contact = add_observation(trace[41080], 'primary contact')
    returns = {}
    for role, clock in ROLE_EXITS.items():
        exit_event, before, after = trace[clock]
        require(exit_event[1] == role and before[0][1:] == after[0][1:], f'bad return of {role}')
        first_read = FIRST_READS[role]
        read = add_observation(trace[first_read], f'first exterior read of {role}')
        pre_read = [i for i in sorted(watched) if clock < i < first_read]
        pre_read = [i for i in pre_read if trace[i][0][1] == role]
        value = after[0][1]
        actions = []
        for i in pre_read:
            require(trace[i][1][0][1] == value, f'pre-read chain discontinuity for {role} at {i}')
            action = add_observation(trace[i], f'pre-read action {i}')
            actions.append({'clock': i, **action})
            value = trace[i][2][0][1]
        require(trace[first_read][1][1][1] == value, f'exterior read did not see return chain {role}')
        contact_value = trace[41080][2][0 if role == 134 else 1][1]
        require(contact_value == before[0][1], f'exit of {role} changed before the outer action')
        returns[role] = {'exit_clock': clock, 'exit_event': exit_event, 'post_exit_value': serial_row(after[0][1]),
                         'pre_read_actions': actions, 'first_exterior_clock': first_read,
                         'first_exterior_action': read, 'final_return': serial_row(candidate['rows'][role])}
    return {'primary_contact': contact, 'returns': returns,
            'courier_events': {clock: trace[clock][0] for clock in COURIER},
            'deep_role46_events': {clock: trace[clock][0] for clock in range(DEEP, DEEP + 8)}}


def helper_targets(word):
    live = set(word['live'])
    main = live | {role + 112 for role in live} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    charts = word['frames']
    ranks = Counter()
    for wire, (start, end) in enumerate(zip(word['initial'], word['final'], strict=True)):
        if wire not in main:
            span_before, span_after = span_mask(charts[start]), span_mask(charts[end])
            require(span_before != span_after and span_before & span_after == span_before,
                    f'invalid helper target on {wire}')
            ranks[len(charts[end]) - len(charts[start])] += 1
    return ranks


def mechanisms_report(before, after):
    return {f'{kind}:{rank}': count for (kind, rank), count in difference(after, before).items()}


def account(base_word, candidate_word, caller, base_replay, candidate_replay, base_invoice):
    events = caller['events']
    calls = [event for event in events if event[0] == 'J']
    count = caller['stages']
    require(caller['schema'] == 'mixed-root-caller/1' and caller['ambient_rank'] == 145 and
            caller['roles'] == 72 and count == 17 and
            [event[1] for event in calls] == list(range(1, count + 1)), 'literal caller call list')
    require(set(caller['types']['A']['ports']).isdisjoint(caller['types']['B']['ports']) and
            sorted(caller['types']['A']['ports'] + caller['types']['B']['ports']) ==
            list(range(len(base_word['ports']))), 'caller port partition')
    p0 = base_replay['paid']
    p1 = candidate_replay['paid']
    t0 = helper_targets(base_word)
    t1 = helper_targets(candidate_word)
    dp = difference(p1, p0)
    dt = difference(t1, t0)
    # Independently bill each altered clock by its source and destination dimensions.
    clock_paid = Counter()
    clock_report = []
    for clock, (old, new) in EXPECTED_EDITS.items():
        ranks = []
        for event, word, sign in ((old, base_word, -1), (new, candidate_word, 1)):
            rank = None
            if event is not None and event[0] == 'MOVE':
                charts = word['frames']
                rank = abs(len(charts[event[3]]) - len(charts[event[2]]))
                clock_paid[rank] += sign
            ranks.append(rank)
        clock_report.append({'clock': clock, 'base_rank': ranks[0], 'candidate_rank': ranks[1]})
    expected_paid = {rank: delta for rank, delta in sorted(clock_paid.items()) if delta}
    require(dp == expected_paid == {1: -2, 2: 2, 3: -1, 4: -1, 5: 1}, 'paid rank delta mismatch')
    require(not dt, 'native helper target delta must vanish')
    dm = mechanisms_report(base_replay['mechanisms'], candidate_replay['mechanisms'])
    require(dm == {f'public_rise:{rank}': delta for rank, delta in dp.items()}, 'mechanism delta mismatch')

    def caller_residual(full, native, label):
        residual = difference(full, {rank: count * n for rank, n in native.items()})
        require(all(n >= 0 for n in residual.values()), f'negative caller residual for {label}')
        return residual

    caller_paid = caller_residual(base_invoice['P'], p0, 'paid')
    caller_targets = caller_residual(base_invoice['T'], t0, 'targets')
    candidate_paid = dict(Counter(caller_paid) + Counter({rank: count * n for rank, n in p1.items()}))
    candidate_targets = dict(Counter(caller_targets) + Counter({rank: count * n for rank, n in t1.items()}))
    result = {'P': candidate_paid, 'T': candidate_targets,
              'S': rank_mass(candidate_targets) - rank_mass(candidate_paid)}
    require(invoice_delta(result, base_invoice) ==
            {'P': {rank: count * n for rank, n in expected_paid.items()}, 'T': {}, 'S': 0},
            'full invoice delta mismatch')
    detail = {'calls': count, 'native_paid_base': dict(p0), 'native_paid_candidate': dict(p1),
              'native_target_base': dict(t0), 'native_target_candidate': dict(t1),
              'per_clock_rank_charges': clock_report, 'native_mechanism_delta': dm,
              'full_mechanism_delta': {key: count * n for key, n in dm.items()},
              'caller_paid_residual': caller_paid, 'caller_target_residual': caller_targets,
              'full_candidate_invoice': result}
    return result, detail


def digest_observations(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()


def check_semantics(base, candidate, watched):
    require(len(base['observed']) == len(candidate['observed']) == 630 and
            base['observed'] == candidate['observed'], 'private/COPY observation mismatch')
    require(len(base['erased']) == len(candidate['erased']) == 74 and
            base['erased'] == candidate['erased'], 'erased row or ownership mismatch')
    require(base['rows'] == candidate['rows'], 'arbitrary-input endpoint mismatch')
    return {'boundary': boundary_report(base, candidate, watched),
            'private_copy_observations': len(candidate['observed']),
            'private_copy_sha256': digest_observations(candidate['observed']),
            'copy_clocks': [clock for clock, trace in candidate['observed'].items() if trace[0][0] == 'COPY'],
            'erased_values_and_owners': len(candidate['erased']),
            'erase_sha256': digest_observations(candidate['erased']),
            'erase_owners': [{'clock': clock, 'register': r, 'init_clock': start, 'chart': chart}
                             for clock, (r, start, chart, _) in candidate['erased'].items()],
            'arbitrary_input_endpoints': len(candidate['rows']),
            'nonzero_endpoint_coefficients': sum(map(len, candidate['rows'])),
            'endpoint_sha256': digest_observations(candidate['rows'])}


def mutation_controls(base_word, candidate_word, tagged, caller, base_replay, candidate_replay,
                      base_invoice, watched):
    def altered_add():
        for clock, event in tagged:
            if clock == 41080:
                event = event.copy()
                event[3] = '-3/4'
            yield clock, event

    wrong = replay(candidate_word, altered_add(), watched)
    exterior_134 = FIRST_READS[134]
    require(wrong['boundary'][exterior_134][1][1][1] !=
            candidate_replay['boundary'][exterior_134][1][1][1], 'primary mutation survived exterior read')
    require(wrong['rows'] != candidate_replay['rows'], 'primary mutation survived arbitrary-input endpoints')

    omitted = {**candidate_replay, 'paid': candidate_replay['paid'].copy()}
    charge_clock = ROLE_EXITS[134]
    charge_event = dict(tagged)[charge_clock]
    charts = candidate_word['frames']
    missing_rank = len(charts[charge_event[3]]) - len(charts[charge_event[2]])
    omitted['paid'][missing_rank] -= 1
    try:
        account(base_word, candidate_word, caller, base_replay, omitted, base_invoice)
    except ValueError as error:
        require(str(error) == 'paid rank delta mismatch', f'unexpected mutation failure: {error}')
    else:
        raise ValueError('missing charge survived invoice gate')
    return {'altered_primary_contact_coefficient': {'clock': 41080, 'rejected_at_exterior': exterior_134,
                                                     'endpoint_difference': True},
            'missing_charge': {'clock': charge_clock, 'rank': missing_rank, 'rejected': True}}


def crossing_report(candidate, peer):
    # The first bound lies above the frozen peer crossing and below the candidate crossing.
    low = Fraction('.0036524238120')
    high = Fraction('.00366')
    net = signed(candidate)
    peer_interval = histogram_bounds(signed(peer), low)
    require(peer_interval[0] > 0 and histogram_bounds(net, low)[1] < 0 and
            histogram_bounds(net, high)[0] > 0, 'candidate did not bracket beyond the peer crossing')
    for _ in range(24):
        middle = (low + high) / 2
        lower, upper = histogram_bounds(net, middle)
        if upper < 0:
            low = middle
        elif lower > 0:
            high = middle
        else:
            break
    require(histogram_bounds(net, low)[1] < 0 and histogram_bounds(net, high)[0] > 0,
            'lost outward crossing signs')
    return {'reference_k': '.0036524238120', 'peer_signed_at_reference': interval_text(peer_interval),
            'candidate_signed_at_reference': interval_text(histogram_bounds(net, Fraction('.0036524238120'))),
            'candidate_crossing_bracket': interval_text((low, high)), 'quantity': 'P(k)-T(k)'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'secondary', 'candidate', 'caller', 'invoice7645', 'invoice7657'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    base_word = load(args.base)
    candidate_word = load(args.candidate)
    caller = load(args.caller)
    secondary_invoice, base_invoice = map(read_invoice, (load(args.invoice7645), load(args.invoice7657)))
    base_sha = canonical_sha(base_word)
    require(base_sha == BASE_SHA, f'unexpected base canonical SHA {base_sha}')
    secondary_sha = canonical_sha(load(args.secondary))
    require(secondary_sha == SECONDARY_SHA, f'unexpected secondary canonical SHA {secondary_sha}')
    require(base_word['schema'] == 'p104-accumulated-block-composition/2', 'unexpected native schema')
    require(invoice_delta(base_invoice, secondary_invoice) ==
            {'P': {1: -17, 2: -17, 3: 17}, 'S': 0, 'T': {}}, 'unexpected peer invoice delta')
    tagged = align(base_word, candidate_word)
    watched = relevant_clocks(base_word['program'])
    base = replay(base_word, enumerate(base_word['program']), watched)
    candidate = replay(candidate_word, tagged, watched)
    semantics = check_semantics(base, candidate, watched)
    candidate_invoice, details = account(base_word, candidate_word, caller, base, candidate, base_invoice)
    pricing = pricing_report(secondary_invoice, candidate_invoice, base_invoice)
    require(all(item['candidate_delta_sign'] == 'lower' for item in pricing.values()),
            'candidate is not cheaper at both frozen references')
    crossing = crossing_report(candidate_invoice, base_invoice)
    mutations = mutation_controls(base_word, candidate_word, tagged, caller, base, candidate, base_invoice, watched)
    clocks = {clock: i for i, (clock, _) in enumerate(tagged)}
    print(json.dumps({'status': 'PASS_INDEPENDENT_NATIVE_AND_INVOICE_DELTA',
                      'canonical_sha256': {'base7657': base_sha, 'secondary7645': secondary_sha,
                                           'candidate': canonical_sha(candidate_word),
                                           'caller': canonical_sha(caller)},
                      'invoice_file_sha256': {'secondary7645': sha256(args.invoice7645.read_bytes()).hexdigest(),
                                              'base7657': sha256(args.invoice7657.read_bytes()).hexdigest()},
                      'base_clock_to_candidate_clock': {clock: clocks.get(clock) for clock in sorted(watched)},
                      'literal': semantics, 'invoice': details, 'pricing': pricing, 'crossing': crossing,
                      'mutation_controls': mutations,
                      'scope': {'literal': 'Exact arbitrary-input native linear maps in literal charts, including all public output rows.',
                                'caller_invoice': 'Full delta by native census and 17 shared call sites. The absolute unchanged caller invoice is the pinned base residual.',
                                'separate_application': 'Physical chart phases, signed caller tensor composition, and absolute caller reconstruction remain with the coordinator application.'}},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
