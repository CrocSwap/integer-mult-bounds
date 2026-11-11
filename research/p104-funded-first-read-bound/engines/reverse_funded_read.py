"""Reverse next-contact census for one funded public helper first read."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER_HEAD = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'WORD.json.gz': 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    'CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'ADMITTED.json': '41b8a189dffeb768e5843446cdc469f9cc2f0aa038d0a593cf2be43aa009a9a3',
}
PROTECTED = {863, 1355, 1568}
CASE_LIMIT = 1101
COOPERATIVE_SECONDS = 18


def unique(rows):
    record = dict(rows)
    if len(rows) != len(record):
        raise ValueError('duplicate JSON key')
    return record


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def checked(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError('changed input: ' + path.name)
    return raw


def roles_touched(event):
    op, field, *args = event
    if op in ('ADD', 'COPY'):
        assert field != args[0]
        return field, args[0]
    assert op in ('INIT', 'CLEAR', 'MOVE', 'SCALE'), event
    return (field,)


def reverse_walk(events, fields, deadline):
    first, second, source_reads = [None] * fields, [None] * fields, {}
    for clock in reversed(range(len(events))):
        if monotonic() >= deadline:
            return first, second, source_reads, clock
        event = events[clock]
        roles = roles_touched(event)
        if event[0] == 'ADD':
            destination, source = roles
            source_reads[source] = (clock, first[destination])
        for field in roles:
            assert 0 <= field < fields
            second[field] = first[field]
            first[field] = clock
    return first, second, source_reads, None


def pivot_reduce(value, pivots):
    while value:
        bit = value.bit_length() - 1
        if bit not in pivots:
            break
        value ^= pivots[bit]
    return value


def audit(word, deadline):
    n = word['public']
    excluded = set(word['live']) | {r + 112 for r in word['live']}
    excluded.update(word['hosted']['X2'] + word['hosted']['Y2'])
    dimensions = tuple(map(len, word['frames']))

    @cache
    def pivots(chart):
        basis = {}
        for row in word['frames'][chart]:
            value = pivot_reduce(row, basis)
            assert value
            basis[value.bit_length() - 1] = value
        return basis

    def strict_inclusion(a, b):
        return dimensions[a] < dimensions[b] and all(
            not pivot_reduce(v, pivots(b)) for v in word['frames'][a])

    helper = {}
    for h, (a, z) in enumerate(zip(word['initial'], word['final'], strict=True)):
        if h not in excluded:
            assert strict_inclusion(a, z), ('invalid productive pair', h, a, z)
            helper[h] = (a, z, dimensions[z] - dimensions[a])
    assert len(helper) <= CASE_LIMIT
    events = word['program']
    first, second, source, unvisited_clock = reverse_walk(events, n + word['owned_fields'], deadline)
    decisions = []
    for h, (a, z, target_rank) in helper.items() if unvisited_clock is None else ():
        if monotonic() >= deadline:
            break
        clock = first[h]
        entry = {'h': h, 'initial': a, 'final': z, 'rank': target_rank,
                 'first': clock, 'next_h': second[h], 'g': None, 'next_g': None}
        if h in PROTECTED:
            verdict = 'protected_h'
        elif target_rank < 2:
            verdict = 'zero_residual_rank'
        elif h not in source or source[h][0] != clock:
            verdict = 'first_not_add_source'
        else:
            event = events[clock]
            _, g, read, coeff, chart = event
            assert read == h and chart == a and Fraction(coeff), ('bad first read', h, clock)
            next_h, next_g = second[h], source[h][1]
            entry.update(g=g, next_g=next_g)
            if g not in helper:
                verdict = 'partner_not_public_productive'
            elif g in PROTECTED:
                verdict = 'protected_g'
            elif next_h is None or events[next_h][0] != 'MOVE':
                verdict = 'helper_next_not_move'
            elif next_g is None or events[next_g][0] != 'MOVE':
                verdict = 'partner_next_not_move'
            else:
                _, hh, ah, ch, oh = events[next_h]
                _, gg, ag, cg, og = events[next_g]
                assert (hh, gg, ah, ag) == (h, g, a, a) and oh is False and og is False
                entry.update(helper_destination=ch, partner_destination=cg)
                if ch != cg:
                    verdict = 'different_destination'
                elif dimensions[ch] != dimensions[a] + 1 or not strict_inclusion(a, ch):
                    verdict = 'not_rank_one_ascent'
                elif not strict_inclusion(ch, z):
                    verdict = 'not_strict_residual'
                else:
                    verdict = 'eligible'
                    entry['key'] = [h, g, clock, next_h, next_g, a, ch, z]
        decisions.append(entry | {'status': verdict})
    remaining = list(helper)[len(decisions):]
    return {'events': len(events), 'visited_events': len(events) if unvisited_clock is None else len(events)-unvisited_clock-1,
            'next_unvisited_reverse_clock': unvisited_clock,
            'helpers': len(helper), 'visited_helpers': len(decisions), 'main_hosted_roles': len(excluded),
            'status': 'EXHAUSTED' if not remaining else 'HIT_TIME_CAP',
            'status_counts': dict(Counter(row['status'] for row in decisions)),
            'productive_rank_histogram': dict(Counter(t for a, z, t in helper.values())),
            'unvisited_roles': remaining,
            'unvisited_rank_histogram': dict(Counter(helper[h][2] for h in remaining if h not in PROTECTED and helper[h][2] >= 2)),
            'survivors': [r['key'] for r in decisions if r['status'] == 'eligible'], 'records': decisions}


def controls():
    old = [['ADD', 1, 0, '3/5', 0], ['MOVE', 1, 0, 1, False], ['MOVE', 0, 0, 1, False],
           ['MOVE', 0, 1, 2, False], ['MOVE', 1, 1, 2, False], ['MOVE', 2, 0, 2, False]]
    word = {'public': 3, 'owned_fields': 0, 'live': [], 'hosted': {'X2': [], 'Y2': []},
            'frames': [[], [1], [1, 2]], 'initial': [0, 0, 0], 'final': [2, 2, 2], 'program': old}
    assert audit(word, float('inf'))['survivors'] == [[0, 1, 0, 2, 1, 0, 1, 2]]
    wrong = word | {'program': [old[0], ['ADD', 2, 1, '-2', 0], *old[1:]]}
    failed = audit(wrong, float('inf'))
    assert not failed['survivors'] and failed['records'][0]['status'] == 'partner_next_not_move'
    earlier = word | {'program': [['ADD', 2, 0, '-2', 0], *old]}
    failed = audit(earlier, float('inf'))
    assert not failed['survivors'] and failed['records'][0]['first'] == 0

    different = word | {'frames': [[], [1], [1, 2], [2]],
                        'program': [old[0], ['MOVE', 1, 0, 3, False], *old[2:4],
                                    ['MOVE', 1, 3, 2, False], old[-1]]}
    failed = audit(different, float('inf'))
    assert not failed['survivors'] and failed['records'][0]['status'] == 'different_destination'

    def forward(values, changed):
        h, g = values[:2], values[2:]
        phase = lambda xy: (-xy[1], xy[0])
        add = lambda a, b: tuple(x + Fraction(3, 5) * y for x, y in zip(a, b, strict=True))
        return (*phase(h), *add(phase(g), phase(h))) if changed else (*phase(h), *phase(add(g, h)))

    columns = [tuple(int(j == i) for j in range(4)) for i in range(4)]
    dirty = (Fraction(7, 3), Fraction(-4, 5), Fraction(-9, 2), Fraction(11, 7))
    assert all(forward(column, False) == forward(column, True) for column in [*columns, dirty])
    def adjoint(values, changed):
        h, g = values[:2], values[2:]
        inverse_phase = lambda xy: (xy[1], -xy[0])
        add = lambda a, b: tuple(x + Fraction(3, 5) * y for x, y in zip(a, b, strict=True))
        head = inverse_phase(add(h, g)) if changed else add(inverse_phase(h), inverse_phase(g))
        return (*head, *inverse_phase(g))

    assert all(adjoint(column, False) == adjoint(column, True) for column in [*columns, dirty])
    return {'dirty_signed_transport_and_adjoint': True, 'earlier_source_read': True,
            'intervening_partner_source': True, 'different_destination': True}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=Path('inputs'))
    parser.add_argument('--price', type=Path)
    parser.add_argument('--price-sha')
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    assert __debug__
    ctl = controls()
    if args.controls_only:
        print(json.dumps(ctl, sort_keys=True))
        return
    if args.price is None or args.price_sha is None:
        parser.error('saved directed price and digest required before decoding')
    deadline = monotonic() + COOPERATIVE_SECONDS
    price = load(checked(args.price, args.price_sha))
    assert price['head'] == HEAD and price.get('caller_head', price.get('caller')) == CALLER_HEAD
    raw = {name: checked(args.inputs / name, digest) for name, digest in PINS.items()}
    admission = load(raw['ADMITTED.json'])
    assert admission['head'] == HEAD and admission['caller_sha256'] == PINS['CALLER.json']
    assert admission['status'] == 'independently_reproduced_comparable'
    caller = load(raw['CALLER.json'])
    assert caller['stages'] == 17
    result = audit(load(gzip.decompress(raw['WORD.json.gz'])), deadline)
    assert result['helpers'] == CASE_LIMIT
    print(json.dumps(result | {'head': HEAD, 'caller_head': CALLER_HEAD, 'price_sha256': args.price_sha,
                               'input_sha256': PINS, 'controls': ctl}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
