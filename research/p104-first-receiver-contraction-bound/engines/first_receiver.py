"""Exact reverse e930 separation of the first retained chart-652 receiver."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    'inputs/PLAN.md': '13224daa1271a10de69dc7c45d105e9518765da9529771a181b5447f70d02ee6',
    'inputs/R29-RESULT.json': '6fa36e6a2b618ad96a6e18389c165dc04f3f987b186d8ce33bdb82bed47ef5b5',
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/7274-WORD.json.gz': '66bc395b599bc0b805c5061bbbd124e2027ad86645c07abe40d0b472fa1a7a2b',
    'inputs/reverse_span.py': 'f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CUT, MOVER, RECEIVER, CHART = 42651, 930, 793, 652
CLOCKS = [42650, 42651, 42692, 42693, 42695, 42697]
OLD_CLOCKS = [42648, 42649, 42690, 42691, 42693, 42695]
EVENTS = [
    ['MOVE', 930, 3, 652, False],
    ['ADD', 793, 930, '1/2', 652],
    ['MOVE', 930, 652, 657, False],
    ['ADD', 1473, 930, '-1', 657],
    ['ADD', 930, 982, '-1', 657],
    ['MOVE', 930, 657, 649, False],
]


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError('duplicate JSON key')
    return obj


def checked(root):
    raw = {path: (root / path).read_bytes() for path in PINS}
    for path, data in raw.items():
        if sha256(data).hexdigest() != PINS[path]:
            raise ValueError(f'changed dependency {path}')
    return raw


def span(basis):
    out = {0}
    for u in basis:
        assert u not in out and 0 < u < 512
        out |= {u ^ v for v in out}
    return out


def literal(word, old, receipt):
    assert len(word['program']) == 76466 and word['public'] == 1501
    assert [word['program'][i] for i in CLOCKS] == EVENTS
    assert [old['program'][i] for i in OLD_CLOCKS] == EVENTS
    assert word['program'][42649] == ['ADD', 1473, 930, '1', 3]
    assert word['program'][42653] == ['MOVE', 793, 652, 653, False]
    assert '[42648,42695,"in_span",1060,5,0]' in dumps(receipt, separators=(',', ':'))
    frames = [word['frames'][label] for label in (3, 652, 657, 649)]
    assert list(map(len, frames)) == [0, 2, 6, 7]
    a, b, c, d = map(span, frames)
    assert a < b < c < d
    return frames


def bank_at(word, deadline):
    n = word['public']
    state = word['final'] + [None] * word['owned_fields']
    fresh_copy = set()
    bank = None
    for clock in range(len(word['program']) - 1, -1, -1):
        if clock % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError('literal reverse chart walk')
        op, d, *args = word['program'][clock]
        assert 0 <= d < len(state) and (d not in fresh_copy or op == 'INIT')
        if op == 'MOVE':
            left, right, owned = args
            assert state[d] == right and owned == (d >= n)
            state[d] = left
        elif op == 'INIT':
            assert d >= n and state[d] == args[0]
            state[d] = None
            fresh_copy.discard(d)
        elif op == 'CLEAR':
            assert d >= n and state[d] is None
            state[d] = args[0]
        else:
            assert op in ('SCALE', 'ADD', 'COPY') and state[d] == args[-1]
            assert Fraction(args[-2])
            if op in ('ADD', 'COPY'):
                src = args[0]
                assert d != src and 0 <= src < len(state) and state[src] == args[-1]
            if op == 'COPY':
                assert d >= n
                fresh_copy.add(d)
        if clock == CUT:
            assert state[MOVER] == state[RECEIVER] == CHART
            bank = [role for role, frame in enumerate(state) if frame == CHART and role != MOVER]
    assert not fresh_copy and state == word['initial'] + [None] * word['owned_fields']
    assert bank is not None and RECEIVER in bank
    return bank


def evaluate(word, requests, engine, deadline, input_axis):
    rows = engine['transpose_prefix'](word, requests, sum(map(len, requests.values())), deadline)
    return [Fraction(coeffs.get(input_axis, 0), den) for coeffs, den in rows]


def controls(engine, deadline):
    # Both exact controls traverse negative SCALE, ADD, and dirty COPY rules.
    toy = {'public': 3, 'owned_fields': 1, 'program': [
        ['SCALE', 0, '-2', 0], ['INIT', 3, 0], ['COPY', 3, 0, '1/2', 0],
        ['ADD', 1, 3, '-1', 0], ['CLEAR', 3, 0], ['ADD', 2, 1, '3', 0],
    ]}
    assert evaluate(toy, {4: [(0, 0), (2, 1), (3, 2)], 5: [(1, 3)]},
                    engine, deadline, 0) == [-2, 0, -1, 1]
    return ['nonzero required and zero donor', 'retained owned donor nonzero', 'signed COPY and CLEAR']


def stop(*_):
    raise TimeoutError('hard 20-second cap')


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    signal(SIGALRM, stop)
    alarm(20)
    deadline = monotonic() + 19
    raw = checked(args.root)
    engine = run_path(str(args.root / 'inputs/reverse_span.py'))
    tests = controls(engine, deadline)
    if args.controls_only:
        print(dumps(tests))
        return
    result = {'head': HEAD, 'caller': CALLER, 'pins': PINS, 'caps': {'cases': 1, 'seconds': 20},
              'cut': CUT, 'chart': CHART, 'source': MOVER, 'receiver': RECEIVER, 'controls': tests}
    try:
        word, old = (loads(decompress(raw[f'inputs/{n}-WORD.json.gz']), object_pairs_hook=unique)
                     for n in ('7334', '7274'))
        receipt = loads(raw['inputs/R29-RESULT.json'], object_pairs_hook=unique)
        frames = literal(word, old, receipt)
        bank = bank_at(word, deadline)
        roles = [MOVER, *bank]
        values = evaluate(word, {CUT: [(role, i) for i, role in enumerate(roles)]}, engine, deadline, MOVER)
        source, donors = values[0], values[1:]
        required = source / 2
        assert len(donors) == len(bank)
        result.update(frames=frames, old_clocks=OLD_CLOCKS, current_clocks=CLOCKS,
                      events=EVENTS, receiver_next_clock=42653, case_count=1,
                      source_coordinate=str(source), required_coordinate=str(required),
                      receiver_old_coordinate=str(donors[bank.index(RECEIVER)]),
                      bank_public=[r for r in bank if r < word['public']],
                      bank_owned=[r for r in bank if r >= word['public']],
                      bank_values=[[r, str(v)] for r, v in zip(bank, donors, strict=True)],
                      disposition='excluded' if required and not any(donors) else 'unresolved')
    except TimeoutError as exc:
        result.update(disposition='unresolved', reason=str(exc), case_count=0)
    finally:
        alarm(0)
    print(dumps(result, indent=2, sort_keys=True))
    if result['case_count'] == 0:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
