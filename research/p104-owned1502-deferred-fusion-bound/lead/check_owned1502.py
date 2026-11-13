"""Test the fixed deferred repair against the entire edited chart-905 bank."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
from sys import stderr, version_info

ROOT = Path(__file__).resolve().parent.parent
PINS = {
    'inputs/7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'inputs/7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    'inputs/7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/gate.py': 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9',
}
OMIT, CUT, OWNER, OBSERVER = 33141, 43317, 1502, 1489


def binary_span(frame):
    span = {0}
    for generator in frame:
        span |= {value ^ generator for value in span}
    assert len(span) == 2 ** len(frame)
    return span


def evaluate(row, probe):
    return sum(coefficient * probe.get(i, 0) for i, coefficient in row.items())


def separator(pivots, residual):
    coordinate = min(residual)
    assert coordinate not in pivots
    probe = {coordinate: 1 / residual[coordinate]}
    for pivot, (vector, _) in sorted(pivots.items(), reverse=True):
        value = -evaluate(vector, probe)
        if value:
            probe[pivot] = value
    return probe


def mentions(row, role):
    return row[1] == role or (row[0] in ('ADD', 'COPY') and row[2] == role)


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    alarm(30)
    inputs = {path: (ROOT / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in inputs.items()} == PINS
    raw = decompress(inputs['inputs/7481-WORD.json.gz'])
    assert sha256(raw).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = json.loads(raw)
    tape = word['program']
    events = {
        33140: ['MOVE', OWNER, 541, 534, True],
        OMIT: ['ADD', OBSERVER, OWNER, '4', 534],
        33142: ['MOVE', OWNER, 534, 117, True],
        33143: ['ADD', 629, OWNER, '2', 117],
        33145: ['ADD', 732, OWNER, '1', 117],
        33149: ['MOVE', OWNER, 117, 594, True],
        43315: ['MOVE', 152, 1057, 905, False],
        43316: ['MOVE', OBSERVER, 534, 905, False],
        CUT: ['ADD', 152, OBSERVER, '-1/2', 905],
    }
    assert all(tape[i] == event for i, event in events.items())
    assert [i for i in range(OMIT + 1, CUT) if mentions(tape[i], OBSERVER)] == [43316]
    frames = word['frames']
    assert [len(frames[i]) for i in (117, 534, 541)] == [5, 6, 7]
    assert binary_span(frames[117]) < binary_span(frames[534]) < binary_span(frames[541])
    caller = json.loads(inputs['inputs/7113-CALLER.json'])
    app = json.loads(inputs['inputs/7481-APPLICATION.json'])
    copies = caller['stages']
    assert copies == sum(event[0] == 'J' for event in caller['events']) == 17
    power = run_path(str(ROOT / 'inputs/pricing.py'))['power_bounds']
    low, high = map(Fraction, app['directed_crossing_bracket'])
    gross_lower = copies * (2 - power(2, low)[1])
    gross_upper = copies * (2 - power(2, high)[0])
    assert Fraction('0.08584222521755123') <= gross_lower <= gross_upper <= Fraction('0.08584222521755124')
    print('PASS_PINNED_CHRONOLOGY_AND_PRICE', file=stderr, flush=True)

    exact = run_path(str(ROOT / 'inputs/gate.py'))
    _, active, _ = exact['census'](word, CUT)
    bank = sorted(role for role, chart in active.items() if chart == 905)
    assert {152, OBSERVER} <= set(bank)
    read = exact['exact_cut_rows']
    target, = read(tape[:OMIT], [OWNER], word['public'])
    old = read(tape[:CUT], bank, word['public'])
    edited = [row.copy() for row in old]
    index = bank.index(OBSERVER)
    for j, coefficient in target.items():
        exact['add'](edited[index], j, -4 * coefficient)
    print(f'BANK_ROWS_READY {len(bank)}', file=stderr, flush=True)
    pivots = exact['basis'](edited)
    residual, coefficients = exact['representation'](pivots, target)
    result = {
        'bank': bank, 'bank_rank': len(pivots), 'cut': CUT, 'omitted_add': OMIT,
        'pins': PINS, 'caps': {'cases': 1, 'seconds': 30},
        'tested': 1, 'unresolved': [], 'signed_paid_delta': {1: -34, 2: 17},
        'gross_interval': [gross_lower, gross_upper],
    }
    if residual:
        probe = separator(pivots, residual)
        assert evaluate(target, probe) == 1
        responses = {role: evaluate(row, probe) for role, row in zip(bank, edited, strict=True)}
        assert not any(responses.values())
        old_responses = {role: evaluate(row, probe) for role, row in zip(bank, old, strict=True)}
        assert old_responses[OBSERVER] == 4
        assert all(not val for role, val in old_responses.items() if role != OBSERVER)
        result.update(status='EXACT_FIXED_LATE_BANK_EXCLUSION', probe=probe, historical_response='1',
                      old_bank_responses={role: str(value) for role, value in old_responses.items()},
                      edited_bank_responses={role: str(value) for role, value in responses.items()})
    else:
        rebuilt = {}
        for j, scalar in coefficients.items():
            for column, value in edited[j].items():
                exact['add'](rebuilt, column, scalar * value)
        assert rebuilt == target
        result.update(status='EXACT_RATIONAL_SUPPORT',
                      representation={bank[j]: v for j, v in coefficients.items()},
                      final_self_coefficient=1 + 4 * coefficients.get(index, 0))
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == '__main__':
    main()
