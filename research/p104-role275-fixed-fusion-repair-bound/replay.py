"""Reproduce the two fixed role-275 repair obstructions and directed price."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz', 'PROVENANCE.json',
    'gate.py', 'pricing.py', 'check_probe.py', 'verify_275_reverse.py', 'delayed77.py',
    'receipts/SOURCE-FORWARD.json', 'receipts/SOURCE-REVERSE.json', 'receipts/DELAYED.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def check_source(forward, reverse):
    assert forward['status'] == 'UNIT_PROBE_EXCLUDES_SOURCE_BANK'
    assert reverse['status'] == 'PASS_REVERSE_SOURCE_SEPARATOR'
    assert forward['cut'] == reverse['cut'] == 31438
    assert forward['bank_size'] == len(reverse['bank']) == len(set(reverse['bank'])) == 898
    assert forward['probe'] == reverse['input'] == {'100': 1}
    assert forward['old_target_value'] == reverse['required_donor_value'] == '1'
    assert forward['nonzero_available'] == reverse['nonzero_bank_coefficients'] == {}


def check_targets(matrix):
    a, b = [list(map(Fraction, row)) for row in matrix]
    assert a[0] * b[1] - a[1] * b[0] == 1


def check_delayed(delayed):
    assert delayed['status'] == 'EXACT_ROLE77_ONE_ARRIVAL_EXCLUDED'
    assert delayed['case_cap'] == delayed['cases_completed'] == 1
    assert delayed['runner_cap_seconds'] == 30
    assert (delayed['read'], delayed['after'], delayed['chart']) == (31452, 31459, 312)
    assert delayed['roles'] == [275, 77]
    assert delayed['direct_arrival'] == 'old275_before_ADD31452_minus_x100'
    assert delayed['fixed_rank'] == 1 and delayed['quotient_rank'] == 2
    assert delayed['target_determinant'] == '1'
    assert delayed['witnesses'] == [
        {'probe': {'100': '1'}, 'old_inputs': ['1', '0'], 'old_outputs': ['1', '-1/2']},
        {'probe': {'77': '1'}, 'old_inputs': ['0', '1'], 'old_outputs': ['1', '1/2']},
    ]
    check_targets([row['old_outputs'] for row in delayed['witnesses']])


def check_price(inputs, delayed):
    word = loads(decompress(inputs['7481-WORD.json.gz']), object_pairs_hook=unique)
    caller = loads(inputs['7113-CALLER.json'], object_pairs_hook=unique)
    tape, frames = word['program'], word['frames']
    assert tape[31441] == ['MOVE', 275, 3, 93, False]
    assert tape[31450] == ['MOVE', 275, 93, 312, False]
    assert [len(frames[destination]) - len(frames[source]) for source, destination in
            ((3, 93), (93, 312), (3, 312))] == [1, 1, 2]
    copies = sum(event[0] == 'J' for event in caller['events'])
    assert caller['stages'] == copies == 17
    assert delayed['signed_paid_delta'] == {'1': -2 * copies, '2': copies}
    assert delayed['signed_productive_delta'] == {}
    lo, hi = map(Fraction, delayed['directed_gross'])
    assert Fraction('0.0858422252175512') < lo <= hi < Fraction('0.0858422252175513') < copies


def expect_failure(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('negative control unexpectedly passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    assert set(pins) == INPUTS
    inputs = {name: (ROOT / name).read_bytes() for name in sorted(INPUTS)}
    for name, raw in inputs.items():
        check_hash(raw, pins[name])
    receipts = []
    for script, name in (('check_probe.py', 'SOURCE-FORWARD.json'),
                         ('verify_275_reverse.py', 'SOURCE-REVERSE.json'),
                         ('delayed77.py', 'DELAYED.json')):
        result = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    forward, reverse, delayed = receipts
    check_source(forward, reverse)
    check_delayed(delayed)
    check_price(inputs, delayed)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: check_source(dict(forward, nonzero_available={'1': '1'}), reverse))
    expect_failure(lambda: check_targets([['1', '-1/2'], ['1', '-1/2']]))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_ROLE275_FIXED_FUSION_REPAIRS: two exact exclusions, three frozen replays')


if __name__ == '__main__':
    main()
