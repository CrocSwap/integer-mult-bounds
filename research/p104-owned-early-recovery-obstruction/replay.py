"""Verify the exact one-cut obstruction against independent sparse and dense replays."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7481-APPLICATION.json', '7481-WORD.json.gz',
    'PROVENANCE.json', 'early_cut.py', 'early_cut_dense.py', 'gate.py',
    'pricing.py', 'receipts/RESULT.json', 'receipts/INDEPENDENT.json',
}
PROBE = {'34': '-1', '129': '-1', '1336': '-1', '1501': '1'}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(data, digest):
    assert sha256(data).hexdigest() == digest, 'changed bytes'


def evaluate(row, probe):
    return sum(Fraction(value) * Fraction(probe.get(index, '0')) for index, value in row.items())


def check_separator(sparse, probe):
    assert all(evaluate(row, probe) == 0 for row in sparse['source_rows'])
    assert evaluate(sparse['target_rows']['recover'], probe) == 1
    assert evaluate(sparse['target_rows']['1336'], probe) == -1
    assert evaluate(sparse['target_rows']['1563'], probe) == 1
    assert evaluate(sparse['target_rows']['outward_ADD42502'], probe) == 0


def compare(sparse, dense):
    assert sparse['status'] == 'EXACT_EARLY_CUT_EXCLUSION'
    assert dense['status'] == 'rationally_inconsistent'
    assert sparse['case'] == [1533, 38139, 42500, 1031]
    assert dense['case'] == {'role': 1533, 'cut': 42500, 'chart': 1031,
                             'cap_seconds': 30, 'cases_completed': 1}
    assert sparse['case_cap'] == 1 and sparse['runner_cap_seconds'] == 30
    assert sparse['coframe'] == dense['role_order'] and len(sparse['coframe']) == 18
    assert sparse['extra_coordinate'] == dense['extra_input_column'] == 1501
    assert sparse['dirty_column'] == dense['extra_column'] == {'1336': '1', '1563': '-1'}
    assert sparse['changed_INIT_COPY_guards'] == dense['dirty_guard_failures'] == []
    assert dense['exterior_extra_column'] == {}
    assert sparse['bank_rank'] == sparse['old_rank'] == dense['source_rank'] == 18
    assert sparse['rank_with_recovery'] == dense['required_rank'] == dense['combined_rank'] == 19
    assert sparse['separating_inputs']['recover'] == PROBE
    check_separator(sparse, PROBE)
    expected = {'recover_extra': '1', 'restore_1336': '-1', 'restore_1563': '1'}
    assert dense['separators'] == {
        label: {'required_value': value, 'source_values': ['0'] * 18,
                'public_and_extra_input_probe': PROBE} for label, value in expected.items()
    }
    for role, row in zip(sparse['coframe'], sparse['source_rows']):
        old = sparse['target_rows'][str(role)]
        assert old == dense['old_rows'][str(role)]
        assert row == old | ({'1501': sparse['dirty_column'][str(role)]}
                             if str(role) in sparse['dirty_column'] else {})
    prior = dense['prior_outward_add']
    assert (prior['clock'], prior['destination'], prior['extra_coefficient']) == (42495, 1336, '1')
    assert evaluate(prior['old_row'], PROBE) == -1
    assert dense['nonzero_owned_clears'] == [[42497, 1562, 1031, '1']]
    assert dense['later_outward_add']['old_source_term'] == sparse['target_rows']['outward_ADD42502']
    assert dense['representations']['retained_add_42502_term'] == {'1533': '-1/2'}


def early_price(inputs):
    word = loads(decompress(inputs['7481-WORD.json.gz']), object_pairs_hook=unique)
    assert word['program'][42487] == ['MOVE', 1533, 597, 1031, True]
    rank = len(word['frames'][1031]) - len(word['frames'][597])
    copies = loads(inputs['7113-CALLER.json'], object_pairs_hook=unique)['stages']
    application = loads(inputs['7481-APPLICATION.json'], object_pairs_hook=unique)
    lo, hi = map(Fraction, application['directed_crossing_bracket'])
    power_bounds = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    assert rank == 4 and copies == 17 and 0 < lo < hi < 1
    upper = copies * power_bounds(rank, lo)[1]
    assert upper == Fraction('42285665351942530030470451339513892297517714895199/625000000000000000000000000000000000000000000000')
    assert upper < Fraction('67.657064563109')
    return upper


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
    for script, receipt in (('early_cut.py', 'RESULT.json'), ('early_cut_dense.py', 'INDEPENDENT.json')):
        replayed = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                       capture_output=True, timeout=32).stdout
        actual = loads(replayed, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{receipt}'], object_pairs_hook=unique)
        receipts.append(actual)
    sparse, dense = receipts
    compare(sparse, dense)
    upper = early_price(inputs)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: check_separator(sparse, PROBE | {'1501': '0'}))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print(f'PASS_OWNED_EARLY_CUT: one case, rank 18 vs 19, early gross upper {upper}')


if __name__ == '__main__':
    main()
