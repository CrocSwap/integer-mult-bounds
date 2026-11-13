"""Independent exact cycle-polynomial and eigenphase interpolation check."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
from json import dumps, loads
from pathlib import Path
from signal import alarm

ROOT = Path(__file__).resolve().parent
CALLER = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
CHILD = 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b'


def cyclic_product(left, right):
    return [sum(left[i] * right[(k - i) % 4] for i in range(4)) for k in range(4)]


def poly_power(factor, exponent):
    result = [1, 0, 0, 0]
    for _ in range(exponent):
        result = cyclic_product(result, factor)
    return result


def main():
    assert __debug__
    alarm(30)
    raw = (ROOT / '7113-CALLER.json').read_bytes()
    child = (ROOT / '7113-signed-child.py').read_bytes()
    assert sha256(raw).hexdigest() == CALLER
    assert sha256(child).hexdigest() == CHILD
    caller = loads(raw)
    roles = (68, 69)
    for role, clock in zip(roles, (1339, 1340)):
        found = []
        for index, event in enumerate(caller['events']):
            if event[0] == 'J':
                assert role not in event[3][:2]
            elif event[0] == 'B':
                count = 2 if event[1] in {'ADD', 'SWAP', 'QUERY'} else 1
                if role in event[2:2 + count]:
                    found.append((index, event))
        assert found == [(clock, ['B', 'IDLE_ODD', role, [8], -1])]
    ports = caller['types']['B']['ports']
    assert ports[0] == 15 and len(ports) == 8
    plus, minus = [1, 1, 0, 0], [1, 0, 0, 1]
    old = cyclic_product(poly_power(plus, 8), minus)
    base_core = poly_power(plus, 9)
    residuals = [512 - old[even] - old[odd] for even, odd in product((0, 2), (1, 3))]
    # E has one freely chosen value on each parity. Any pair can be
    # interpolated by a=(even+odd)/2 and b=(even−odd)/2 over the Gaussian field.
    for even, odd in product((0, 2), (1, 3)):
        roots = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        a = [(x + y) * Fraction(1, 2) for x, y in zip(roots[even], roots[odd])]
        b = [(x - y) * Fraction(1, 2) for x, y in zip(roots[even], roots[odd])]
        zero_phases = [p for p in range(4) if tuple(x + (-1)**p * y for x, y in zip(a, b)) == roots[p]]
        assert zero_phases == sorted([even, odd])
    core_ranks = []
    for n in range(10):
        multiplicities = cyclic_product(poly_power(plus, 9 - n), poly_power(minus, n))
        core_ranks.extend(512 - count for count in multiplicities)
    needed = min(a + b for a, b in product(residuals, repeat=2))
    capacity = max(core_ranks)
    assert needed == 480 and capacity == 392 and needed > capacity
    assert 2 * min(residuals) == needed
    # A dropped lane changes the decision. This exercises the two-return obligation.
    assert min(residuals) == 240 < capacity
    print(dumps({'port':15, 'roles':roles, 'old_phase_counts':old, 'core_phase_counts':base_core,
                 'per_lane_residual_rank_choices':residuals, 'minimum_two_lane_rank':needed,
                 'maximum_core_rank':capacity, 'single_lane_control_survives':True,
                 'status':'PASS_INDEPENDENT_SIGNED_IDLE_RANK'}, indent=2, sort_keys=True))
    alarm(0)


if __name__ == '__main__':
    main()
