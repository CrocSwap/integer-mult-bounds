#!/usr/bin/env python3
"""Exact adaptive-grid injectivity audit. woklerx/Codex; Apache-2.0."""
import hashlib
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def rounded(v, bits):
    z = v * (1 << bits) + F(1, 2)
    return F(z.numerator // z.denominator, 1 << bits)

def independent_leaf_increment(bits):
    # Literal length-one recurrence, without the imported arithmetic helpers.
    power = rounded(F(1, 4), bits)
    seed = rounded(1 / (1 - power), bits)
    power = rounded(F(1, 4), bits)
    value = 1 + rounded(power * seed, bits)
    return rounded(-value / 4, bits)

def run():
    for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'source drift')
    spec = importlib.util.spec_from_file_location('adaptive_grid_vendor', ROOT / 'research/dirty-prefix-precision/vendor/pr628/dirty.py')
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)
    factors = [(False, (F(1, 4), F(0)), F(1))]
    increments = {p: independent_leaf_increment(p) for p in (4, 5)}
    need(increments == {4: F(-5, 16), 5: F(-11, 32)}, 'independent leaf increments')

    def execute(y, bits, sign=1):
        x = [vendor.c.ONE]
        target = [y]
        vendor.compose(x, target, factors, [], [vendor.c.ONE], F(1, 2), bits, 1, sign)
        need(x == [vendor.c.ONE], 'source restored')
        need(target == [(y[0] + sign * increments[bits], y[1])], 'independent source recurrence')
        return target[0]

    # Fixed precision positive controls, over the actual admitted grids.
    fixed = 0
    for q, imag in itertools.product(range(-128, 130), (F(-7, 16), F(0), F(5, 16))):
        y = (F(q, 32), imag)
        for bits in ((4, 5) if q % 2 == 0 else (5,)):
            need(execute(execute(y, bits), bits, -1) == y, 'same-grid inverse')
            fixed += 1

    collisions = stored = forgotten = 0
    for k, imag in itertools.product(range(-64, 65), (F(-7, 16), F(0), F(5, 16))):
        y_even, y_odd = (F(2*k, 32), imag), (F(2*k+1, 32), imag)
        out_even, out_odd = execute(y_even, 4), execute(y_odd, 5)
        need(y_even != y_odd and out_even == out_odd, 'distinct inputs collide')
        need(out_even == (F(2*k-10, 32), imag), 'whole integer collision family')
        need(execute(out_even, 4, -1) == y_even and execute(out_odd, 5, -1) == y_odd, 'stored branch restores')
        # Coarsest-compatible policy recomputed from either output is bits4.
        need((out_odd[0] * 16).denominator == 1, 'output selects coarse branch')
        need(execute(out_odd, 4, -1) == y_even != y_odd, 'forgotten branch loses odd input')
        collisions += 1
        stored += 2
        forgotten += 1

    # Independent finite-period check of the general residue-translation theorem.
    # Brute images over a padded integer interval are compared to algebraic fibers.
    residue_policies = bijective = 0
    for modulus in range(2, 6):
        for residues in itertools.product(range(modulus), repeat=modulus):
            shifts = tuple(a + modulus * (r-2) for r, a in enumerate(residues))
            counts = [sum((r+shifts[r]) % modulus == s for r in range(modulus)) for s in range(modulus)]
            bound = 3*modulus + max(abs(a) for a in shifts)
            images = {}
            for q in range(-bound, bound+1):
                y = q + shifts[q % modulus]
                images.setdefault(y, []).append(q)
            for y in range(-2*modulus, 2*modulus+1):
                candidates = sorted(y-a for r, a in enumerate(shifts) if (y-a) % modulus == r)
                need(candidates == images.get(y, []), 'independent integer fiber census')
                need(len(candidates) == counts[y % modulus], 'residue-fiber multiplicity')
            bijective += all(n == 1 for n in counts)
            residue_policies += 1
    need((residue_policies, bijective) == (3412, 152), 'complete residue-policy census')

    # Admission is meaningful: coarse execution cannot silently accept fine-only dirt.
    try:
        execute((F(1, 32), F(0)), 4)
    except ValueError as exc:
        need('fixed grid data' in str(exc), 'expected source admission rejection')
    else:
        raise ValueError('off-grid coarse input accepted')
    return {
        'status': 'PASS_ADAPTIVE_GRID_INJECTIVITY',
        'actual_increments': {str(k): str(v) for k, v in increments.items()},
        'counterexample': {'even_input': '0', 'odd_input': '1/32', 'same_output': '-5/16', 'source': '1'},
        'actual_collision_pairs': collisions,
        'fixed_grid_positive_inverse_cases': fixed,
        'stored_branch_inverse_cases': stored,
        'forgotten_branch_failures': forgotten,
        'general_residue_policy_cases': residue_policies,
        'bijective_residue_policy_cases': bijective,
        'off_grid_admission_controls': 1,
        'current_fixed_grid_bug': False,
        'new_kappa': False,
    }

if __name__ == '__main__':
    result = run()
    path = HERE / 'EXPECTED.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'receipt mismatch')
    print(result['status'], result['actual_collision_pairs'], 'actual admitted collision pairs')
