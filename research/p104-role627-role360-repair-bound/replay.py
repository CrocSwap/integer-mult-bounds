"""Verify the exact role-360 one-arrival bound and its optimistic tariff."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz',
    'PROBES.json', 'PROVENANCE.json', 'gate.py', 'pricing.py', 'role627.py',
    'verify_627_probes.py', 'receipts/INDEPENDENT.json', 'receipts/RESULT.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def check_targets(matrix):
    a, b = [list(map(Fraction, row)) for row in matrix]
    assert a[0] * b[1] - a[1] * b[0] == -1


def compare(primary, independent):
    assert primary['status'] == 'FIXED_ROLE360_REPAIR_EXCLUDED'
    assert independent['status'] == 'PASS_INDEPENDENT_CHART836_QUOTIENT'
    assert primary['case_cap'] == independent['case_cap'] == independent['cases_completed'] == 1
    assert primary['runner_cap_seconds'] == independent['runner_cap_seconds'] == 30
    assert primary['cut'] == independent['cut'] == 43805 and independent['chart'] == 836
    assert primary['direct_source'] == [627, independent['early_bypass_clock']] == [627, 32947]
    assert independent['target_roles'] == [360, 627]
    bank = [406, 1168, 1289, 1430]
    assert primary['fixed_roles'] == independent['fixed_bank'] == bank
    assert (primary['rank'], primary['union']) == (5, 7)
    expected = [({'244': '-1', '623': '2'}, ['0', '1']),
                ({'4': '2', '30': '16/5', '1430': '1/2'}, ['1', '0'])]
    assert [(row['input'], [str(value) for value in row['old_targets'][::-1]])
            for row in primary['certificate']] == expected
    assert [(row['probe'], row['required_old_outputs']) for row in independent['witnesses']] == expected
    for row in independent['witnesses']:
        assert row['fixed_bank'] == {str(role): '0' for role in bank}
        assert row['bypassed_early_627'] == '0'
    check_targets([row['required_old_outputs'] for row in independent['witnesses']])
    assert independent['target_determinant'] == '-1' and independent['zero_control'] == ['0', '0']


def check_price(inputs, primary):
    word = loads(decompress(inputs['7481-WORD.json.gz']), object_pairs_hook=unique)
    caller = loads(inputs['7113-CALLER.json'], object_pairs_hook=unique)
    frames = {chart: len(word['frames'][chart]) for chart in (3, 117, 836, 222)}
    tape = word['program']
    old = [tuple(tape[clock][2:4]) for clock in (32947, 43804, 32949, 44298)]
    assert old == [(3, 117), (117, 836), (3, 117), (117, 222)]
    new = [(3, 836), (3, 117), (117, 836), (836, 222)]
    assert [frames[b] - frames[a] for a, b in old] == primary['old_paid_ranks'] == [5, 1, 5, 3]
    assert [frames[b] - frames[a] for a, b in new] == primary['new_paid_ranks'] == [6, 5, 1, 2]
    assert sum(event[0] == 'J' for event in caller['events']) == caller['stages'] == 17
    lo, hi = map(Fraction, primary['gross_signed_before_repairs'])
    assert Fraction('0.0488') < lo <= hi < Fraction('0.0489') < 17


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
    for script, name in (('role627.py', 'RESULT.json'), ('verify_627_probes.py', 'INDEPENDENT.json')):
        result = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    primary, independent = receipts
    compare(primary, independent)
    check_price(inputs, primary)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: check_targets([['1', '0'], ['1', '0']]))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_ROLE627_ROLE360_REPAIR: one exact case, bank rank 5, required union rank 7')


if __name__ == '__main__':
    main()
