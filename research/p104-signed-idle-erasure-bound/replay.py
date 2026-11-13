"""Replay and compare two exact width-one signed idle rank certificates."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {
    '7113-CALLER.json', '7113-signed-child.py', '7481-APPLICATION.json', 'pricing.py',
    'signed_idle_gate.py', 'verify_idle_rank.py', 'PROVENANCE.json',
    'receipts/FINITE.json', 'receipts/INDEPENDENT.json',
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def check(raw, digest):
    assert sha256(raw).hexdigest() == digest, 'changed bytes'


def compare(finite, independent):
    assert finite['cases_completed'] == 1 and finite['status'] == 'rank_exclusion'
    assert independent['status'] == 'PASS_INDEPENDENT_SIGNED_IDLE_RANK'
    assert finite['case'] == {'events': [1339, 1340], 'roles': [68, 69], 'stage': 8,
                              'width': 1, 'port': 15, 'cap_seconds': 30}
    assert finite['case']['port'] == independent['port']
    assert finite['case']['roles'] == independent['roles']
    assert finite['source_phase_multiplicities'] == independent['old_phase_counts']
    assert finite['core_phase_multiplicities'] == independent['core_phase_counts']
    assert finite['minimum_residual_rank'] == independent['minimum_two_lane_rank'] == 480
    assert finite['maximum_core_displacement_rank'] == independent['maximum_core_rank'] == 392
    assert independent['single_lane_control_survives']
    assert finite['prospective_paid_delta'] == {'9': -8}
    assert finite['prospective_productive_delta'] == {}
    low, high = map(Fraction, finite['gross_directed_before_ancillary_costs'])
    assert 71 < low <= high < 72


def expect_failure(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('mutated input or receipt passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = parse((ROOT / 'PINS.json').read_bytes())
    assert set(pins) == FILES
    inputs = {name: (ROOT / name).read_bytes() for name in sorted(FILES)}
    for name, raw in inputs.items():
        check(raw, pins[name])
    finite = parse(run([executable, '-I', '-B', str(ROOT / 'signed_idle_gate.py')],
                       check=True, capture_output=True, timeout=32).stdout)
    independent = parse(run([executable, '-I', '-B', str(ROOT / 'verify_idle_rank.py')],
                            check=True, capture_output=True, timeout=32).stdout)
    assert finite == parse(inputs['receipts/FINITE.json'])
    assert independent == parse(inputs['receipts/INDEPENDENT.json'])
    compare(finite, independent)
    raw = inputs['7113-CALLER.json']
    expect_failure(lambda: check(bytes([raw[0] ^ 1]) + raw[1:], pins['7113-CALLER.json']))
    expect_failure(lambda: parse('{"caller":1,"caller":2}'))
    expect_failure(lambda: compare(finite, dict(independent, minimum_two_lane_rank=240)))
    print('PASS_SIGNED_IDLE_ERASURE_BOUND: one finite case, rank 480 exceeds 392')


if __name__ == '__main__':
    main()
