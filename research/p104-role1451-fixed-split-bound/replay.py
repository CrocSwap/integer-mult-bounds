"""Reproduce and cross-check the two exact fixed role-1451 split gates."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
CASES = (
    ('check_1451_input.py', 'LATE-REVERSE.json'),
    ('verify_1451_input.py', 'LATE-FORWARD.json'),
    ('check_1451_early.py', 'EARLY-REVERSE.json'),
    ('forward_1451_early.py', 'EARLY-FORWARD.json'),
)
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz',
    'PROVENANCE.json', 'gate.py', 'pricing.py',
} | {path for runner, receipt in CASES for path in (runner, f'receipts/{receipt}')}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def compare_late(reverse, forward):
    assert reverse['status'] == 'FIXED_INPUT_GATE_EXCLUDED'
    assert forward['status'] == 'PASS_FIXED_1451_INPUT_WITNESS'
    assert reverse['cut'] == forward['cut'] == 39826 and forward['chart'] == 737
    assert reverse['bank'] == forward['bank'] == [1451, 1495, 1501]
    assert reverse['allowed_initial'] == forward['allowed_initial_roles'] == [1451, 1495]
    assert reverse['case_cap'] == forward['case_cap'] == forward['cases_completed'] == 1
    assert reverse['runner_cap_seconds'] == forward['runner_cap_seconds'] == 30
    assert reverse['solution_uv'] is None
    assert reverse['evidence'] == {'constraints': {'3': '-1', '716': '1'}, 'contradiction': '-1'}
    assert reverse['evidence']['constraints'] == forward['probe']
    assert forward['old_bank_values'] == ['1', '0', '0']
    assert forward['opposite_control'] == ['-1', '0', '0']
    assert forward['zero_control'] == ['0', '0', '0']


def compare_early(reverse, forward):
    assert reverse['status'] == 'FIXED_FIRST_OUTWARD_READ_EXCLUDED'
    assert forward['status'] == 'PASS_LITERAL_FORWARD_FIRST_OUTWARD_SEPARATOR'
    assert (reverse['cut'], reverse['first_outward_read']) == (37945, 37946)
    assert reverse['bank'] == [992, 1451]
    assert reverse['cases'] == forward['case_cap'] == 1
    assert reverse['runner_cap_seconds'] == forward['runner_cap_seconds'] == 30
    assert reverse['probe'] == forward['probe'] == {'716': 1}
    assert reverse['exposed_input'] == {'1451': '1'} and forward['exposed_x1451'] == '0'
    at_read = forward['observations']['37946']
    assert at_read['451'] == [595, '1'] and at_read['992'] == [737, '0']
    assert at_read['1451'] == [737, '1']
    assert reverse['probe_on_old_992'] == int(at_read['992'][1])
    assert reverse['probe_on_omitted_451'] == int(at_read['451'][1])
    assert str(reverse['required_old_outward_increment']) == forward['old_outward_increment'] == '-1'
    assert forward['zero_control'] is True


def check_price(inputs, early):
    word = loads(decompress(inputs['7481-WORD.json.gz']), object_pairs_hook=unique)
    caller = loads(inputs['7113-CALLER.json'], object_pairs_hook=unique)
    frames = [len(word['frames'][chart]) for chart in (595, 737, 529)]
    assert frames == [1, 4, 7]
    copies = sum(event[0] == 'J' for event in caller['events'])
    assert copies == caller['stages'] == 17
    assert early['paid_signed_delta'] == {}
    assert early['productive_signed_delta'] == {'3': 2 * copies, '6': -copies}
    low, high = map(Fraction, early['gross_raw'])
    assert Fraction('0.25649690068') < low <= high < Fraction('0.25649690070') < copies


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
    for script, name in CASES:
        result = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    late_reverse, late_forward, early_reverse, early_forward = receipts
    compare_late(late_reverse, late_forward)
    compare_early(early_reverse, early_forward)
    check_price(inputs, early_reverse)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: compare_late(late_reverse, dict(late_forward, old_bank_values=['1', '1', '0'])))
    expect_failure(lambda: compare_early(early_reverse, dict(early_forward, old_outward_increment='0')))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_ROLE1451_FIXED_SPLIT_BOUND: two exact cuts and four source-bound receipts')


if __name__ == '__main__':
    main()
