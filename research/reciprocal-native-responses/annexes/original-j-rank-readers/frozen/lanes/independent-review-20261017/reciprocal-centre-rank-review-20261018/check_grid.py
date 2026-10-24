#!/usr/bin/env python3
"""Check the signed scan and nested words on a common integer grid."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def need(test, label):
    if not test:
        raise ValueError(label)


def signed(value, width):
    return value-(1 << width) if value >> (width-1) else value


def divide13(value, width):
    source = value % (1 << width)
    carry, output = 0, 0
    for pos in range(width):
        bit = (source >> pos) & 1
        out = (bit-carry) % 2
        output |= out << pos
        carry = (carry+13*out-bit)//2
        need(0 <= carry < 13, 'Division carry range')
    result = signed(output, width)
    accepted = carry == 13*(result < 0)-(value < 0)
    return accepted, result


def multiply13(value, width):
    source = value % (1 << width)
    carry, output = 0, 0
    for pos in range(width):
        bit = (source >> pos) & 1
        total = 13*bit+carry
        output |= (total % 2) << pos
        carry = total//2
        need(0 <= carry < 13, 'Multiplication carry range')
    result = signed(output, width)
    accepted = carry == 13*(value < 0)-(result < 0)
    return accepted, result


scan_inputs = 0
for width in range(1, 15):
    limit = 1 << (width-1)
    for value in range(-limit, limit):
        good, quotient = divide13(value, width)
        need(good == (value % 13 == 0), 'Exact signed division acceptance')
        if good:
            need(13*quotient == value, 'Exact signed quotient')
        good, product = multiply13(value, width)
        need(good == (-limit <= 13*value < limit), 'Signed multiplication overflow')
        if good:
            need(product == 13*value, 'Exact signed product')
        scan_inputs += 1


def valuation13(value):
    if value == 0:
        return None
    value = abs(value)
    exponent = 0
    while value % 13 == 0:
        value //= 13
        exponent += 1
    return exponent


grid_cases = []
for remaining in range(5):
    levels = remaining+1
    odd_budget = 8*levels
    binary_budget = 8*levels
    root_scale = 13**odd_budget * 2**binary_budget
    state = [[root_scale*int(i == j) for j in range(8)] for i in range(8)]
    observations = {'events': 0, 'divisions': 0, 'max_height': 0,
                    'completed_calls': 0, 'max_active_levels': 0}

    def observe(active):
        height = max([0]+[max(0, odd_budget-v)
                          for row in state for value in row
                          if (v := valuation13(value)) is not None])
        need(height <= 8*active, 'Active-path height bound')
        observations['max_height'] = max(observations['max_height'], height)
        observations['max_active_levels'] = max(observations['max_active_levels'], active)
        observations['events'] += 1

    def scale_row(row, numerator, divisor, active):
        need(all(value % divisor == 0 for value in state[row]), 'Exact grid division')
        state[row] = [numerator*(value//divisor) for value in state[row]]
        observations['divisions'] += int(divisor == 13)
        observe(active)

    def shear(row, source, sign, active):
        need(all(value % 2 == 0 for value in state[source]), 'Binary guard')
        state[row] = [x+sign*(y//2) for x, y in zip(state[row], state[source])]
        observe(active)

    def run(depth, target, sign, active):
        entry = [row[:] for row in state]
        if depth:
            for row in range(8):
                scale_row(row, -1 if row < 4 else -13, 13 if row < 4 else 1, active)
            child_target = depth % 8
            run(depth-1, child_target, 1, active+1)
            run(depth-1, child_target, -1, active+1)
            for row in range(8):
                scale_row(row, -13 if row < 4 else -1, 1 if row < 4 else 13, active)
        source = (target+4) % 8
        shear(target, source, sign, active)
        expected = [row[:] for row in entry]
        need(all(value % 2 == 0 for value in entry[source]), 'Endpoint binary guard')
        expected[target] = [x+sign*(y//2) for x, y in zip(entry[target], entry[source])]
        need(state == expected, 'Every completed child has its dyadic endpoint')
        observations['completed_calls'] += 1

    run(remaining, 0, 1, 1)
    need(all(value % 13**odd_budget == 0 for row in state for value in row),
         'Exact final root unscaling')
    grid_cases.append({'active_levels': levels, 'odd_budget': odd_budget,
                       'binary_budget': binary_budget, **observations})

need(1 % 13 != 0, 'Unscaled finest-grid input is rejected')
value = 13**2
for _ in range(2):
    need(value % 13 == 0, 'First rational child calls')
    value //= 13
need(value % 13 != 0, 'Rational completed children invalidate the depth-only budget')
need((-13**7) % 13**8 != 0, 'Unfinished rational root cannot be unscaled')

out = {
    'status': 'PASS_INDEPENDENT_ODD_GRID_COMPOSITION_CHECKS',
    'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
    'signed_scan_widths': [1, 14],
    'signed_inputs_checked_for_each_scan': scan_inputs,
    'nested_integer_basis_cases': grid_cases,
    'negative_controls': ['unscaled finest-grid numerator',
                          'three rational completed children with a two-level budget',
                          'final unscaling before a dyadic root endpoint'],
    'scope': 'Exact signed scans and test trees. The general active-path bound is proved in ODD-GRID-COMPOSITION.md. These trees are not an emitted supplier controller.'
}
(HERE / 'GRID-CHECKS.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
print(out['status'])
