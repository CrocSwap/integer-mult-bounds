"""Verify all nineteen terminal receiver bounds and their exact source closure."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz',
    'PROVENANCE.json', 'gate.py', 'pricing.py', 'terminal_sparse.py', 'terminal_dense.py',
    'receipts/AGREEMENT.json', 'receipts/CONTINUATION.json', 'receipts/INDEPENDENT.json',
    'receipts/TERMINAL.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def check_case(old, new):
    assert new['case'] == [old[key] for key in ('rank', 'move', 'role', 'read', 'clear')]
    assert new['bank'] == sorted(old['bank']) and new['recipient'] == old['receiver']
    assert all(new[key] == old[key] for key in ('chart', 'bank_rank', 'augmented_rank'))
    assert new['scope_status'] == 'excluded' and old['residual']
    assert new['augmented_rank'] == new['bank_rank'] + 1
    assert new['owned_value_on_probe'] == '1' and Fraction(new['required_add_on_probe'])
    assert new['separating_original_inputs']
    assert new['bank_values_on_probe'] == ['0'] * len(new['bank'])


def compare(early, later, independent, agreement):
    assert early['status'] == later['status'] == 'FIXED_BANK_SCREEN'
    assert independent['status'] == 'PASS_INDEPENDENT_TERMINAL_DENSE'
    population = independent['population']
    assert early['population'] == later['population'] == population and len(population) == 19
    assert len({tuple(case) for case in population}) == 19
    assert len(early['tested']) == early['case_cap'] == 8
    assert len(later['tested']) == later['case_cap'] == 11
    assert early['unresolved'] == population[8:] and later['unresolved'] == []
    assert independent['cases_completed'] == independent['case_cap'] == 19
    assert independent['cap_seconds'] == 30 and not independent['unresolved'] and not independent['survivors']
    expected = early['tested'] + later['tested']
    records = independent['records']
    assert len(records) == len(expected) == 19
    for old, new in zip(expected, records):
        check_case(old, new)
    assert Counter(row['rank'] for row in expected) == {1: 9, 2: 4, 3: 1, 4: 4, 6: 1}
    gross = [tuple(map(Fraction, row['gross_before_repairs'])) for row in expected]
    assert all(0 < low <= high for low, high in gross)
    assert sum(high for _, high in gross) < Fraction('711.417')
    assert agreement == {'status': 'PASS_EXACT_SCOPE_AND_RANK_AGREEMENT', 'cases': 19,
                         'survivors': 0, 'unresolved': 0, 'rank_differences': 0}


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
    for script, arguments, name in (('terminal_sparse.py', ['--first-eight'], 'TERMINAL.json'),
                                    ('terminal_sparse.py', ['--remaining-eleven'], 'CONTINUATION.json'),
                                    ('terminal_dense.py', [], 'INDEPENDENT.json')):
        result = run([executable, '-I', '-B', str(ROOT / script), *arguments], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    early, later, independent = receipts
    agreement = loads(inputs['receipts/AGREEMENT.json'], object_pairs_hook=unique)
    compare(early, later, independent, agreement)
    word = inputs['7481-WORD.json.gz']
    old, new = early['tested'][0], independent['records'][0]
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: check_case(old, dict(new, augmented_rank=new['bank_rank'])))
    expect_failure(lambda: check_case(old, dict(new, required_add_on_probe='0')))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_TERMINAL_OWNED_RECEIVER: 19 exact cases, zero survivors and zero unresolved')


if __name__ == '__main__':
    main()
