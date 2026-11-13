"""Authenticate and replay the exact fixed-cut owned productive-helper gate."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {'gate.py', 'verify_exterior.py', '7113-CALLER.json', '7481-APPLICATION.json',
         '7481-WORD.json.gz', 'pricing.py', 'PROVENANCE.json', 'receipts/RESULT.json',
         'receipts/INDEPENDENT.json'}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check(data, digest):
    assert sha256(data).hexdigest() == digest, 'changed bytes'


def compare(sparse, dense):
    assert sparse['status'] == 'EXACT_FIXED_CUT_EXCLUSION'
    assert sparse['cases_completed'] == sparse['case_cap'] == 1
    assert sparse['coframe'] == dense['coframe']
    assert sparse['cut_dirty_column'] == sparse['exterior_dirty_column'] == {'1336': '1', '1563': '-1'}
    assert dense['exterior'] == [[1336, 1031, '1', 42495], [1563, 1031, '-1', 42491]]
    assert sparse['lifetime'][:3] == [dense[key] for key in ('source', 'start', 'cut')]
    assert not sparse['dirty_guards']
    assert sparse['restoration'] is None and not sparse['necessary_survived']
    assert sparse['stock_count'] == 19 and sparse['stock_rank'] == 56
    assert sparse['changed_full_paid'] == {} and sparse['changed_full_productive'] == {'7': 17}
    lo, hi = map(Fraction, sparse['gross_range'])
    assert Fraction('118.1584595438059') < lo <= hi < Fraction('118.1584595438061')
    assert Fraction(sparse['whole_stock_optimistic_upper']) < Fraction('947.4502523754607')


def expect_failure(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('mutated input or receipt passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    assert set(pins) == FILES
    inputs = {name: (ROOT / name).read_bytes() for name in sorted(FILES)}
    for name, raw in inputs.items():
        check(raw, pins[name])
    receipts = []
    for engine, receipt in (('gate.py', 'RESULT.json'), ('verify_exterior.py', 'INDEPENDENT.json')):
        found = run([executable, '-I', '-B', str(ROOT / engine)], check=True,
                    capture_output=True, timeout=32).stdout
        actual = loads(found, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{receipt}'], object_pairs_hook=unique)
        receipts.append(actual)
    sparse, dense = receipts
    compare(sparse, dense)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: compare(sparse, dict(dense, exterior=dense['exterior'][:1])))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_OWNED_PRODUCTIVE_CUT: one exact case, two chart-1031 exterior values, zero survivors')


if __name__ == '__main__':
    main()
