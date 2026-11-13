"""One exact spectrum and price gate for #7113 Type B caller events 1339/1340."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from json import dumps, loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
PINS = {
    '7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    '7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases_completed': 0, 'cap_seconds': 30}))
    exit(124)


def spectrum(signs):
    return Counter(sum(bit * sign for bit, sign in zip(bits, signs)) % 4
                   for bits in product((0, 1), repeat=len(signs)))


def main():
    signal(SIGALRM, timeout)
    alarm(30)
    assert __debug__
    data = {name: (ROOT / name).read_bytes() for name in PINS}
    assert {name: sha256(content).hexdigest() for name, content in data.items()} == PINS
    caller = loads(data['7113-CALLER.json'])
    application = loads(data['7481-APPLICATION.json'])
    events = caller['events']
    pair = (1339, 1340)
    lanes = (68, 69)
    assert caller['stages'] == 17 and caller['ambient_rank'] == 145
    assert [events[index] for index in pair] == [['B', 'IDLE_ODD', lane, [8], -1] for lane in lanes]
    ports = caller['types']['B']['ports']
    assert ports == [15, 17, 27, 34, 35, 42, 47, 55]
    for index, event in enumerate(events):
        if event[0] == 'J':
            assert not set(lanes).intersection(event[3][:2])
        elif event[0] == 'B' and index not in pair:
            roles = event[2:4] if event[1] in ('ADD', 'SWAP', 'QUERY') else event[2:3]
            assert not set(lanes).intersection(roles)
    # For the pinned binary C, Walsh vectors (1,1) and (1,-1) have
    # eigenvalues 1 and i. Integer Gaussian numerators are over 2.
    child_source = ROOT / '7113-signed-child.py'
    assert sha256(child_source.read_bytes()).hexdigest() == CHILD_PIN
    child = run_path(str(child_source))
    gate = child['C']
    for eig, vec in (((1, 0), (1, 1)), ((0, 1), (1, -1))):
        assert [tuple(sum(gate[row][j][k] * vec[j] for j in range(2)) for k in range(2))
                for row in range(2)] == [tuple(2 * z * v for z in eig) for v in vec]
    source = spectrum((1,) * 8 + (-1,))
    core = spectrum((1,) * 9)
    assert core == Counter({phase: sum(comb(9, k) for k in range(phase, 10, 4)) for phase in range(4)})
    assert all(spectrum((1,) * (9 - n) + (-1,) * n) == Counter({(p - n) % 4: v for p, v in core.items()})
               for n in range(10))
    assert source == Counter({(p - 1) % 4: v for p, v in core.items()})
    volume = 2**9
    # One E value applies to both eigenphases of each parity. It can
    # match at most the more populous phase of that parity.
    erasure_matches = max(source[0], source[2]) + max(source[1], source[3])
    required = 2 * (volume - erasure_matches)
    capacity = volume - min(core.values())
    assert required == 480 and capacity == 392 and required > capacity
    assert application['paid_calls'] == 110519 and application['productive_calls'] == 22461
    low, high = map(Fraction, application['directed_crossing_bracket'])
    power_bounds = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    gross = [len(ports) * power_bounds(9, high)[0], len(ports) * power_bounds(9, low)[1]]
    assert 71 < gross[0] <= gross[1] < 72
    # Root-of-unity filtering bounds every phase occupancy at n>=9
    # within 1/32 of one quarter: 2^{-n/2-1} <= 1/32 for n>=8.
    phase_error = Fraction(1, 32)
    all_width_need = 2 * (1 - 2 * (Fraction(1, 4) + phase_error))
    all_width_cap = 1 - (Fraction(1, 4) - phase_error)
    assert all_width_need == Fraction(7, 8) > all_width_cap == Fraction(25, 32)
    receipt = {
        'status': 'rank_exclusion', 'case': {'width': 1, 'port': ports[0], 'stage': 8,
                                             'events': pair, 'roles': lanes, 'cap_seconds': 30},
        'cases_completed': 1, 'pins': PINS | {'7113-signed-child.py': CHILD_PIN},
        'source_phase_multiplicities': [source[p] for p in range(4)],
        'core_phase_multiplicities': [core[p] for p in range(4)],
        'old_lane_volume': volume, 'minimum_residual_rank': required,
        'maximum_core_displacement_rank': capacity,
        'all_width_minimum_residual_volume': all_width_need,
        'all_width_maximum_core_displacement_volume': all_width_cap,
        'old_full_paid': application['paid_calls'], 'old_full_productive': application['productive_calls'],
        'prospective_paid_delta': {9: -len(ports)}, 'prospective_productive_delta': {},
        'gross_directed_before_ancillary_costs': gross,
    }
    alarm(0)
    print(dumps(receipt, indent=2, sort_keys=True, default=str))


CHILD_PIN = 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b'

if __name__ == '__main__':
    main()
