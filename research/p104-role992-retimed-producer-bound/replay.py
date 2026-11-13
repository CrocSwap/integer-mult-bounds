"""Replay the one retimed producer obstruction and its rank-one tariff."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-WORD.json.gz', 'PROVENANCE.json', 'gate.py',
    'retimed_992.py', 'verify_992_probes.py', 'receipts/INDEPENDENT.json', 'receipts/RESULT.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def check_targets(matrix):
    a, b = [list(map(Fraction, row)) for row in matrix]
    determinant = a[0] * b[1] - a[1] * b[0]
    assert determinant == 1


def compare(primary, independent):
    assert primary['status'] == 'SINGLE_RETIMED_PRODUCER_EXCLUDED'
    assert independent['status'] == 'PASS_INDEPENDENT_RETIMED_992_TWO_PROBES'
    assert primary['case_cap'] == independent['case_cap'] == independent['cases_completed'] == 1
    assert primary['runner_cap_seconds'] == independent['runner_cap_seconds'] == 30
    assert independent['cut'] == 39884 and independent['chart'] == 529
    assert independent['target_roles'] == [992, 913]
    bank = [146, 162, 228, 440, 744, 913, 927, 1197, 1358, 1444, 1451, 1494]
    assert primary['bank'] == independent['receiver_roles'] == bank
    assert (primary['rank'], primary['with_old992'], primary['union']) == (12, 13, 14)
    expected = [({'3': '-2', '22': '-1', '32': '-1'}, ['1', '2']),
                ({'0': '1/2', '146': '-1/2'}, ['0', '1'])]
    assert [(row['probe'], row['required_values']) for row in primary['certificate']] == expected
    assert [(row['input'], row['targets']) for row in independent['witnesses']] == expected
    for row in independent['witnesses']:
        assert row['bank'] == {str(role): '0' for role in bank}
    assert [row['old_transfer'] for row in independent['witnesses']] == ['-4', '-2']
    check_targets([row['targets'] for row in independent['witnesses']])
    assert independent['target_determinant'] == '1' and independent['zero_control'] == ['0', '0']
    assert independent['later_old_arrivals'] == []


def check_price(inputs, primary):
    word = loads(decompress(inputs['7481-WORD.json.gz']), object_pairs_hook=unique)
    caller = loads(inputs['7113-CALLER.json'], object_pairs_hook=unique)
    assert word['program'][39884] == ['MOVE', 1532, 520, 529, True]
    rank = abs(len(word['frames'][529]) - len(word['frames'][520]))
    copies = sum(event[0] == 'J' for event in caller['events'])
    assert rank == primary['removed_native_paid_rank'] == 1
    assert copies == caller['stages'] == 17
    assert primary['signed_gross_raw'] == primary['new_rank1_charge_raw'] == copies


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
    for script, name in (('retimed_992.py', 'RESULT.json'), ('verify_992_probes.py', 'INDEPENDENT.json')):
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
    expect_failure(lambda: check_targets([['1', '2'], ['1', '2']]))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_RETIMED_ROLE992_PRODUCER: one exact case, bank rank 12, required union rank 14')


if __name__ == '__main__':
    main()
