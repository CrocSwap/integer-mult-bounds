"""Price and test six frozen terminal public helper retargets."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'R100-GEOMETRY.json': '075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64',
    'R92-PRICE.json': '05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    '7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
ANCHORS = {205: 45975, 532: 46018, 969: 57024, 1081: 44622, 1250: 55971, 1453: 45725}
EVENTS = 76466
SECONDS = 20


def decode(raw):
    def unique(pairs):
        value = dict(pairs)
        if len(value) != len(pairs):
            raise ValueError('duplicate JSON key')
        return value
    return loads(raw, object_pairs_hook=unique)


def pin(path, digest):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest, ('changed input', path.name)
    return raw


def signed(paid, targets):
    result = targets.copy()
    result.subtract(paid)
    return result


def price(root):
    g = decode(pin(root / 'R100-GEOMETRY.json', PINS['R100-GEOMETRY.json']))
    b = decode(pin(root / 'R92-PRICE.json', PINS['R92-PRICE.json']))
    pin(root / 'pricing.py', PINS['pricing.py'])
    assert g['head'] == b['head'] == HEAD and b['caller_head'] == CALLER
    assert len(b['endpoint_cohort']) == 615
    stock = {}
    for role, count in sorted((int(k), v) for k, v in g['moves'].items()):
        pairs = [x for x in g['pairs'] if x['key'][2] == role]
        assert len(pairs) == count - 1
        last = max(pairs, key=lambda row: row['key'][1])
        if role in b['endpoint_cohort'] and last['charts'][1:] == [207, 127] and last['ranks'][1] == 1:
            stock[role] = last['key'][1]
    assert stock == ANCHORS and len(set(stock.values())) == 6
    paid, targets = (Counter({int(k): v for k, v in b[name].items()})
                     for name in ('old_paid', 'old_targets'))
    cost = run_path(str(root / 'pricing.py'))['cost']
    base = signed(paid, targets)
    delta = {1: 17, 8: 17, 9: -17}
    assert (sum(paid.values()), sum(targets.values())) == (110519, 22461)
    assert sum(r*n for r, n in base.items()) == 1424
    quotes = {}
    for label in ('old_crossing_upper', 'probe', 'moonshot'):
        k = Fraction(b[label])
        old = cost(base, k)
        gross = cost(delta, k)
        one = cost(signed(paid - Counter({1:17}), targets + Counter({8:17}) - Counter({9:17})), k)
        six = cost(signed(paid - Counter({1:102}), targets + Counter({8:102}) - Counter({9:102})), k)
        quotes[label] = {name: [str(x) for x in value] for name, value in (
            ('old_margin', old), ('one_edit_gross', gross), ('one_edit_margin', one),
            ('six_edit_gross', (6*gross[0], 6*gross[1])), ('six_edit_margin', six),
            ('one_edit_one_additional_raw_paid_rank_one', tuple(x - 1 for x in one)))}
        quotes[label]['kappa'] = str(k)
    assert Fraction(quotes['probe']['one_edit_margin'][0]) > 0
    assert Fraction(quotes['old_crossing_upper']['one_edit_one_additional_raw_paid_rank_one'][1]) < 0
    assert Fraction(quotes['moonshot']['six_edit_margin'][1]) < 0
    return {'head': HEAD, 'caller_head': CALLER, 'anchors': stock, 'pins': PINS, 'quotes': quotes,
            'old_paid': paid, 'old_targets': targets, 'paid_count': [110519, 110502, 110417],
            'productive_count': 22461, 'signed_rank_surplus': 1424, 'copies': 17,
            'delta_paid_per_edit': {1: -17}, 'delta_productive_per_edit': {8: 17, 9: -17},
            'stock_upper_only': 'grants pairwise compatibility and no ancillary paid work',
            'retained_bit_premise': b['retained_bit_premise']}


def span(basis):
    values = {0}
    for x in basis:
        assert x not in values
        values.update(y ^ x for y in tuple(values))
    return values


def inspect(word, anchors, inner, outer, initial, event_cap, deadline):
    public = word['public']
    fixed = set(word['live']) | {role + 112 for role in word['live']}
    fixed.update(word['hosted']['X2'], word['hosted']['Y2'])
    a, b, c = (span(word['frames'][i]) for i in (initial, inner, outer))
    assert a < b < c and len(c) == 2*len(b)
    active = {}
    complete = {}
    visited = 0
    program = word['program']
    assert len(program) == event_cap
    for clock, event in enumerate(program):
        if monotonic() > deadline:
            break
        visited += 1
        op, dst, *args = event
        src = args[0] if op in ('ADD', 'COPY') else None
        for role in (dst, src):
            if role not in anchors:
                continue
            terminal = anchors[role]
            if clock < terminal:
                continue
            if clock == terminal:
                assert role < public and role not in fixed
                assert word['initial'][role] == initial and word['final'][role] == outer
                assert event == ['MOVE', role, inner, outer, False]
                active[role] = []
                continue
            assert role in active
            access = 'source' if role == src else 'destination'
            if op == 'SCALE':
                assert Fraction(args[0]) and args[1] == outer
            elif op in ('ADD', 'COPY'):
                assert args[-1] == outer
            else:
                raise AssertionError(('later MOVE or public lifetime operation', clock, event))
            active[role].append([clock, access, event])
    if visited == len(program):
        assert active.keys() == anchors.keys()
        for role, events in sorted(active.items()):
            blocking = [x for x in events if x[2][0] in ('ADD', 'COPY')]
            complete[role] = {'terminal_clock': anchors[role], 'post_terminal_contacts': events,
                              'binary_contacts': len(blocking), 'first_binary_contact': blocking[0] if blocking else None,
                              'status': 'fixed_other_field_wrong_chart' if blocking else 'literal_suffix_survivor'}
    return {'events_visited': visited, 'first_unvisited_event': visited if visited < event_cap else None,
            'dispositions': complete, 'unresolved': sorted(anchors.keys() - complete.keys())}


def controls():
    word = dict(public=2, live=[], hosted={'X2': [], 'Y2': []}, frames=[[], [1], [1,2]],
                initial=[0,2], final=[2,2], program=[['MOVE', 0, 1, 2, False], ['SCALE', 0, '-2', 2]])
    assert inspect(word, {0:0}, 1, 2, 0, 2, float('inf'))['dispositions'][0]['status'] == 'literal_suffix_survivor'
    blocked = word | {'program': word['program'] + [['ADD', 1, 0, '1/2', 2]]}
    assert inspect(blocked, {0:0}, 1, 2, 0, 3, float('inf'))['dispositions'][0]['first_binary_contact'][1] == 'source'
    blocked = word | {'program': word['program'] + [['ADD', 0, 1, '1/2', 2]]}
    assert inspect(blocked, {0:0}, 1, 2, 0, 3, float('inf'))['dispositions'][0]['first_binary_contact'][1] == 'destination'
    assert inspect(word, {0:0}, 1, 2, 0, 2, 0)['unresolved'] == [0]
    return ['nonzero unary suffix remains legal', 'source ADD blocks', 'destination ADD blocks', 'cap preserves unresolved']


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('mode', choices=['price', 'support', 'controls'])
    cli.add_argument('--inputs', type=Path)
    cli.add_argument('--price-sha')
    args = cli.parse_args()
    if args.mode == 'controls':
        print(dumps(controls()))
        return
    if args.inputs is None:
        cli.error('--inputs is required')
    if args.mode == 'price':
        result = price(args.inputs)
    else:
        if args.price_sha is None:
            cli.error('--price-sha is required for support')
        def stop(*_):
            raise TimeoutError('20 second hard cap')
        signal(SIGALRM, stop)
        alarm(SECONDS)
        deadline = monotonic() + SECONDS - 1
        try:
            receipt = decode(pin(Path(__file__).resolve().with_name('PRICE.json'), args.price_sha))
            assert receipt == decode(dumps(price(args.inputs)))
            raw = pin(args.inputs / '7334-WORD.json.gz', PINS['7334-WORD.json.gz'])
            clear = decompress(raw)
            assert sha256(clear).hexdigest() == PAYLOAD, "changed uncompressed native word"
            word = decode(clear)
            result = inspect(word, ANCHORS, 207, 127, 3, EVENTS, deadline)
        except TimeoutError:
            result = {'hard_timeout': True, 'unresolved': sorted(ANCHORS)}
        finally:
            alarm(0)
        result |= {'head': HEAD, 'caller_head': CALLER, 'price_sha256': args.price_sha,
                   'case_cap': len(ANCHORS), 'runner_seconds_cap': SECONDS,
                   'event_cap': EVENTS, 'controls': controls(), 'input_sha256': PINS}
    print(dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
