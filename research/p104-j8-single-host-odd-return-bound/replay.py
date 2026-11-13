"""Reproduce the J8 two-sector rank obstruction with two exact engines."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = {
    '7113-CALLER.json', '7113-signed-child.py', '7481-APPLICATION.json',
    '7481-WORD.json.gz', 'PROVENANCE.json', 'independent.py', 'independent_j8.py',
    'j8_odd_return.py', 'physical_binding.py', 'pricing.py', 'upstream_application.py',
    'receipts/INDEPENDENT.json', 'receipts/RESULT.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def check_hash(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def check_sector(lead, independent):
    assert lead['width'] == independent['sector_witness_width'] == 2
    assert independent['sector_pair'] == [1, -1]
    assert lead['central_walsh_bits'] == ['00', '11']
    assert independent['sector_walsh_slices'] == [[0, 0], [1, 1]]
    assert lead['body_walsh_bits'] == '0' * 16
    assert lead['body_phase'] == independent['shared_nonzero_body'] == 1


def check_ranks(lead, independent):
    assert lead['host_rank'] == independent['host_odd_rank'] == 2
    assert lead['required_rank'] == independent['required_odd_rank'] == 3
    host = [[0, -2], [1, 0]]
    target = [row + [0] for row in host] + [[0, 0, 2]]
    assert [[int(value) for value in row] for row in lead['host_difference']] == host
    assert lead['required_difference'] == independent['required_odd_difference']
    assert [[int(value) for value in row] for row in lead['required_difference']] == target
    assert lead['host_minor'] == '2'
    assert lead['target_minor'] == independent['required_odd_determinant'] == '4'
    assert independent['single_removed_rail_control_rank'] == 2


def compare(lead, independent):
    assert lead['status'] == 'EXACT_SECTOR_IDENTICAL_HOST_EXCLUSION'
    assert independent['status'] == 'PASS_INDEPENDENT_J8_FIXED_FIBRE_RANK'
    assert lead['cases_completed'] == independent['cases_completed'] == 1
    assert lead['cap_seconds'] == 30
    assert lead['port'] == 15 and lead['host_roles'] == [36, 37]
    assert lead['idle_clock'] == 1339 and lead['host_clock'] == 1423 and lead['extra_role'] == 68
    assert independent['case'] == {'port': 15, 'stage': 8, 'rail': 68, 'host_roles': [36, 37],
                                   'idle_event': 1339, 'host_event': 1423, 'cap_seconds': 30}
    assert lead['native_main_pair'] == independent['native_roles'] == [17, 129]
    assert lead['axes'] == independent['physical_axes'] == [81] + [1 << axis for axis in range(65, 73)]
    assert independent['axis_gram'] == [[int(i == j) for i in range(9)] for j in range(9)]
    check_sector(lead, independent)
    check_ranks(lead, independent)
    lo, hi = map(Fraction, lead['gross_full_caller'])
    assert 71 < lo <= hi < 72
    assert lead['paid_delta_if_built_at_every_port'] == {'9': -8} and lead['productive_delta'] == {}


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
    for script, name in (('j8_odd_return.py', 'RESULT.json'), ('independent_j8.py', 'INDEPENDENT.json')):
        result = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=32).stdout
        actual = loads(result, object_pairs_hook=unique)
        assert actual == loads(inputs[f'receipts/{name}'], object_pairs_hook=unique)
        receipts.append(actual)
    lead, independent = receipts
    compare(lead, independent)
    word = inputs['7481-WORD.json.gz']
    expect_failure(lambda: check_hash(bytes([word[0] ^ 1]) + word[1:], pins['7481-WORD.json.gz']))
    expect_failure(lambda: check_sector(lead, dict(independent, sector_pair=[1, 1])))
    expect_failure(lambda: check_ranks(dict(lead, required_rank=2), independent))
    expect_failure(lambda: loads('{"word":0,"word":1}', object_pairs_hook=unique))
    print('PASS_J8_SINGLE_HOST_ODD_RETURN: one physical width-two case, required rank 3, host rank 2')


if __name__ == '__main__':
    main()
