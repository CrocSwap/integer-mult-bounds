"""Verify the exact fixed-bank producer obstruction with two coefficient engines."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz',
    'PROVENANCE.json', 'gate.py', 'pricing.py', 'producer_screen.py',
    'verify_749_quotient.py', 'receipts/INDEPENDENT.json', 'receipts/RESULT.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(data, digest):
    assert sha256(data).hexdigest() == digest, 'changed bytes'


def compare(primary, independent):
    assert primary['status'] == 'ONE_LATE_SCALAR_EXCLUDED'
    assert independent['status'] == 'EXACT_RECEIVER_QUOTIENT_EXCLUSION'
    assert primary['case_cap'] == independent['cases_completed'] == 1
    assert independent['case'] == {'role': 749, 'early': 32222, 'cut': 35152,
                                   'late': 35155, 'runner_cap_seconds': 30}
    assert primary['receiver'] == independent['receiver_donors'] == [226, 988, 990, 1345, 1393, 1506, 1514]
    assert primary['rank'] == independent['receiver_rank'] == 6
    assert primary['union'] == independent['receiver_union_rank'] == 8
    assert independent['receiver_quotient_rank'] == 2
    assert primary['probes'] == independent['receiver_probes'] == [{'749': '1'}, {'270': '-3/4', '317': '1'}]
    values = [['1', '0'], ['0', '3/4']]
    assert [[str(value) for value in row] for row in primary['target_values']] == values
    assert independent['receiver_probe_target_values'] == values
    assert independent['source_donors'] == [1343, 1344, 1346, 1347]
    assert independent['source_span_rank'] == 5 and not independent['source_target_representable']
    assert independent['source_target_probe'] == {'230': '-1/4', '749': '1'}
    assert independent['source_probe_target_value'] == '1'
    lo, hi = map(Fraction, primary['gross_before_repairs'])
    assert 33 < lo <= hi < 34


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
    for script, name in (('producer_screen.py', 'RESULT.json'), ('verify_749_quotient.py', 'INDEPENDENT.json')):
        result = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    primary, independent = receipts
    compare(primary, independent)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: compare(primary, dict(independent, receiver_quotient_rank=1)))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_ROLE749_PRODUCER_QUOTIENT: one exact case, fixed receiver rank 6, required union rank 8')


if __name__ == '__main__':
    main()
