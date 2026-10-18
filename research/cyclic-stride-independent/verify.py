#!/usr/bin/env python3
"""Independent finite-geometric resolvent audit of PR628's weighted factor.

Apache-2.0. Prepared for Ryan Pinto / Ambassators with substantial OpenAI
assistance. The oracle does not call the predecessor's arithmetic, recurrence,
Gaussian solve, matrix expansion, kernel preparation, or factor certificates.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import types

Z = tuple[F, F]
Matrix = list[list[Z]]
ZERO: Z = (F(0), F(0))
ONE: Z = (F(1), F(0))
HERE = Path(__file__).resolve().parent
LENGTHS = tuple(range(1, 13)) + (16, 18, 21)
ROOTS: tuple[Z, ...] = ((F(1, 4), F(1, 8)), (F(2), F(-1, 4)))
UNITS: tuple[Z, ...] = (
    ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13)),
    (F(-1), F(0)), (F(0), F(-1)), (F(5, 13), F(-12, 13)),
)
SEED = 79


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def plus(a: Z, b: Z) -> Z:
    return a[0] + b[0], a[1] + b[1]


def minus(a: Z, b: Z) -> Z:
    return a[0] - b[0], a[1] - b[1]


def times(a: Z, b: Z) -> Z:
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def quotient(a: Z, b: Z) -> Z:
    norm = b[0]**2 + b[1]**2
    require(norm != 0, 'singular cycle closure')
    return ((a[0]*b[0] + a[1]*b[1])/norm,
            (a[1]*b[0] - a[0]*b[1])/norm)


def power(a: Z, n: int) -> Z:
    require(type(n) is int and n >= 0, 'nonnegative integer exponent')
    out = ONE
    while n:
        if n & 1:
            out = times(out, a)
        a = times(a, a)
        n >>= 1
    return out


def norm2(a: Z) -> F:
    return a[0]**2 + a[1]**2


def product(values: list[Z]) -> Z:
    out = ONE
    for value in values:
        out = times(out, value)
    return out


def pair_text(a: Z) -> list[str]:
    return [str(a[0]), str(a[1])]


def matrix_digest(a: Matrix) -> str:
    raw = json.dumps([[pair_text(z) for z in row] for row in a],
                     separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def phase_check(phases: list[Z], stride: int) -> None:
    require(bool(phases), 'nonempty phase array')
    require(type(stride) is int, 'integer stride')
    require(all(len(z) == 2 and all(isinstance(v, F) for v in z)
                and norm2(z) == 1 for z in phases), 'exact rational unit phases')


def cycles(length: int, stride: int) -> list[list[int]]:
    """Permutation orbits, with +stride order; supports zero/negative stride."""
    require(type(length) is int and length > 0, 'positive length')
    require(type(stride) is int, 'integer stride')
    unused = set(range(length))
    result = []
    while unused:
        start = min(unused)
        orbit, i = [], start
        while i in unused:
            unused.remove(i)
            orbit.append(i)
            i = (i + stride) % length
        require(i == start, 'cycle closes at its start')
        result.append(orbit)
    require(len(result) == gcd(length, stride), 'gcd cycle census')
    require(all(len(c) == length // gcd(length, stride) for c in result),
            'cycle length census')
    return result


def resolvent(phases: list[Z], stride: int, rho: Z,
              mutation: str | None = None) -> Matrix:
    """Sum rho^(m-1-j) W^j / (h_C-rho^m), independently of scan order."""
    phase_check(phases, stride)
    n = len(phases)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for orbit in cycles(n, stride):
        m = len(orbit)
        holonomy = product([phases[i] for i in orbit])
        if mutation == 'global_holonomy':
            holonomy = product(phases)
        exponent = n if mutation == 'global_length' else m
        denominator = minus(holonomy, power(rho, exponent))
        if mutation == 'omit_closure':
            denominator = ONE
        coefficients = [quotient(power(rho, m-1-j), denominator)
                        for j in range(m)]
        for i in orbit:
            weight, column = ONE, i
            for coefficient in coefficients:
                out[i][column] = plus(out[i][column], times(coefficient, weight))
                weight = times(weight, phases[column])
                column = (column - stride) % n
    return out


def operator(phases: list[Z], stride: int, rho: Z) -> Matrix:
    """Construct W-rho I directly, not from the oracle's cycle decomposition."""
    n = len(phases)
    a = [[ZERO for _ in range(n)] for _ in range(n)]
    for i, tau in enumerate(phases):
        a[i][i] = minus(ZERO, rho)
        j = (i - stride) % n
        a[i][j] = plus(a[i][j], tau)  # Addition matters when stride == 0.
    return a


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Generic exact matrix product; skipping zero terms changes no coverage."""
    n = len(a)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value != ZERO:
                for j, other in enumerate(b[k]):
                    if other != ZERO:
                        out[i][j] = plus(out[i][j], times(value, other))
    return out


def matvec(a: Matrix, x: list[Z]) -> list[Z]:
    out = []
    for row in a:
        value = ZERO
        for entry, component in zip(row, x):
            value = plus(value, times(entry, component))
        out.append(value)
    return out


def check_inverse(a: Matrix, inv: Matrix) -> None:
    identity = [[ONE if i == j else ZERO for j in range(len(a))]
                for i in range(len(a))]
    require(matmul(a, inv) == identity, 'left inverse identity')
    require(matmul(inv, a) == identity, 'right inverse identity')


def dual_phases(phases: list[Z], stride: int) -> list[Z]:
    return [phases[(i + stride) % len(phases)] for i in range(len(phases))]


def rounded_adapter(module, phases: list[Z], stride: int, rho: Z,
                    x: list[Z], bits: int, direction: int,
                    wrong_phase: bool = False) -> list[Z]:
    """Gather / call exact pinned predecessor / scatter, not a paid tape schedule."""
    phase_check(phases, stride)
    require(len(x) == len(phases), 'RHS length')
    require(direction in (-1, 1), 'neighbor direction')
    require(type(bits) is int and bits >= 3, 'closure precision')
    inside = norm2(rho) < 1
    b = rho if inside else quotient(ONE, rho)
    require(norm2(b) <= F(1, 4), 'factor margin beta=1/2')
    # radix=1 suppresses initial scalar scaling to isolate a single factor;
    # this is NOT a certificate of a radix-1 prime-power polynomial.
    state = dict(radix=1, factors=[(inside, b)], beta=F(1, 2), bits=bits)
    result = [ZERO for _ in x]
    for orbit in cycles(len(x), stride):
        order = orbit if direction == 1 else orbit[:1] + orbit[:0:-1]
        local_x = [x[i] for i in order]
        local_phases = [phases[i] for i in order]
        values = module.apply(local_x, state, local_phases, direction,
                              wrong_phase=wrong_phase)
        for i, value in zip(order, values):
            result[i] = value
    return result


def error_ratio_squared(y: list[Z], exact: list[Z], x: list[Z], bits: int) -> F:
    # WEIGHTED-PROOF's single-factor bound, with B an exact modulus upper bound.
    B = max(abs(z[0]) + abs(z[1]) for z in x)
    bound = 7 * (B + 1) * F(1, 1 << bits) / F(1, 2)**3
    return max(norm2(minus(a, b)) for a, b in zip(y, exact)) / bound**2


def hash_check(raw: bytes, expected: str, name: str) -> None:
    require(hashlib.sha256(raw).hexdigest() == expected, 'source hash: ' + name)


def load_source(repo: Path, source: dict, directory: Path):
    for name, expected in source['files'].items():
        reference = source['commit'] + ':' + source['directory'] + '/' + name
        try:
            raw = subprocess.check_output(['git', '-C', str(repo), 'show', reference],
                                          stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            raise ValueError('Missing pinned PR628 git object; run the README fetch command') from exc
        hash_check(raw, expected, name)
        (directory / name).write_bytes(raw)
    # Execute the pinned arithmetic module. Only scan/apply definitions are
    # selected from weighted.py; their ASTs are not rewritten. This omits the
    # unrelated kernel-certification import (and its Python 3.11 requirement).
    spec = importlib.util.spec_from_file_location('pinned_scan_s79', directory / 'scan.py')
    require(spec is not None and spec.loader is not None, 'module loader')
    arithmetic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arithmetic)
    tree = ast.parse((directory / 'weighted.py').read_text())
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in ('scan', 'apply')]
    require([node.name for node in functions] == ['scan', 'apply'], 'exact source function slice')
    module = types.ModuleType('pinned_weighted_s79')
    module.c = arithmetic
    module.F = F
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(directory / 'weighted.py'), 'exec'),
         module.__dict__)
    return module


def controls(module) -> list[dict]:
    # Deliberately asymmetric phases: two different holonomies for L=6,s=2.
    phases = list(UNITS[:6])
    stride, rho = 2, ROOTS[0]
    a = operator(phases, stride, rho)
    correct = resolvent(phases, stride, rho)
    results = []

    def reject(name, operation):
        try:
            operation()
        except ValueError as exc:
            results.append(dict(name=name, rejected=str(exc)))
        else:
            raise ValueError('Negative control accepted: ' + name)

    for name in ('global_holonomy', 'global_length', 'omit_closure'):
        reject(name, lambda name=name: check_inverse(a, resolvent(phases, stride, rho, name)))
    reject('reverse_stride_without_phase_shift',
           lambda: check_inverse(transpose(a), resolvent(phases, -stride, rho)))
    wrong_dual = [(z[0], -z[1]) for z in dual_phases(phases, stride)]
    reject('conjugation_in_bilinear_transpose',
           lambda: check_inverse(transpose(a), resolvent(wrong_dual, -stride, (rho[0], -rho[1]))))
    missing = [row[:] for row in correct]
    for i in cycles(6, stride)[1]:
        missing[i] = [ZERO] * 6
    reject('missing_second_cycle', lambda: check_inverse(a, missing))
    shifted = correct[1:] + correct[:1]
    reject('incorrect_scatter', lambda: check_inverse(a, shifted))
    reject('singular_unit_root', lambda: resolvent([ONE, ONE], 1, ONE))
    reject('nonunit_phase', lambda: resolvent([ONE, (F(1), F(1))], 1, rho))
    reject('empty_array', lambda: resolvent([], 1, rho))
    reject('noninteger_stride', lambda: resolvent(phases, F(1, 2), rho))
    reject('source_hash_mutation', lambda: hash_check(b'bad', hashlib.sha256(b'good').hexdigest(), 'control'))
    if module is not None:
        x = [ONE, ZERO, (F(1, 2), F(1, 4)), ZERO, ONE, (F(-1, 3), F(1, 5))]
        exact = matvec(correct, x)
        wrong = rounded_adapter(module, phases, stride, rho, x, 40, 1, True)
        reject('pinned_wrong_inner_phase_index',
               lambda: require(error_ratio_squared(wrong, exact, x, 40) <= 1, 'factor error bound'))
        reject('RHS_length', lambda: rounded_adapter(module, phases, stride, rho, [], 40, 1))
        reject('underprecision', lambda: rounded_adapter(module, phases, stride, rho, x, 2, 1))
        reject('unseparated_root', lambda: rounded_adapter(module, phases, stride, (F(3, 4), F(0)), x, 40, 1))
    return results


def run(module, source: dict | None) -> dict:
    rng = random.Random(SEED)
    receipt = dict(schema=1, status='PASS_STRIDE_RESOLVENT_AND_DUAL', seed=SEED,
                   source_commit=source['commit'] if source else None,
                   lengths=list(LENGTHS), stride_residues='all, represented also by s-L',
                   roots=[pair_text(r) for r in ROOTS], precisions=[12, 40], cases=[])
    exact_entries = rounded_cases = rounded_coordinates = 0
    signed_checks = zero_cases = multicycle_cases = 0
    max_ratio = F(0)
    max_ratio_case = None
    transcript = hashlib.sha256()
    for n in LENGTHS:
        for stride in range(n):
            phases = [UNITS[rng.randrange(len(UNITS))] for _ in range(n)]
            # Alternating deterministic inputs include denominators not dividing 2^bits.
            dense_x = [(F(rng.randrange(-7, 8), 17), F(rng.randrange(-8, 9), 19))
                       for _ in range(n)]
            basis = [ONE if i == (SEED + stride) % n else ZERO for i in range(n)]
            orbit_data = cycles(n, stride)
            for ri, rho in enumerate(ROOTS):
                a = operator(phases, stride, rho)
                inv = resolvent(phases, stride, rho)
                check_inverse(a, inv)
                dp = dual_phases(phases, stride)
                inv_t = resolvent(dp, -stride, rho)
                require(inv_t == transpose(inv), 'inverse transpose phase/index identity')
                check_inverse(transpose(a), inv_t)
                require(resolvent(phases, stride-n, rho) == inv, 'signed-stride representative')
                signed_checks += 1
                # Four products and one matrix equality are checked entry-by-entry.
                exact_entries += 5*n*n
                zero_cases += int(stride == 0)
                multicycle_cases += int(len(orbit_data) > 1)
                case = dict(length=n, stride=stride, root=ri,
                            phases=[pair_text(z) for z in phases],
                            cycle_count=len(orbit_data), cycle_length=len(orbit_data[0]),
                            holonomies=[pair_text(product([phases[i] for i in c])) for c in orbit_data],
                            inverse_sha256=matrix_digest(inv), dual_sha256=matrix_digest(inv_t))
                receipt['cases'].append(case)
                if module is not None:
                    for dual, pp, ss, oracle in ((False, phases, stride, inv), (True, dp, -stride, inv_t)):
                        for direction in (-1, 1):
                            for bits in (12, 40):
                                for xi, x in enumerate((dense_x, basis)):
                                    exact = matvec(oracle, x)
                                    # Inputs to the adapter are never mutated by gathering.
                                    saved = (pp[:], x[:])
                                    y = rounded_adapter(module, pp, ss, rho, x, bits, direction)
                                    require((pp, x) == saved, 'read-only input preservation')
                                    ratio = error_ratio_squared(y, exact, x, bits)
                                    require(ratio <= 1, 'rounded factor error bound')
                                    rounded_cases += 1
                                    rounded_coordinates += n
                                    tag = [n, stride, ri, dual, direction, bits, xi]
                                    transcript.update(json.dumps([tag, [pair_text(z) for z in y]], separators=(',', ':')).encode())
                                    if ratio > max_ratio:
                                        max_ratio, max_ratio_case = ratio, tag
    # rho=0 is exact W^-1; isolate this degenerate polynomial case explicitly.
    edge_phases = list(UNITS[:6])
    zero_root = resolvent(edge_phases, 2, ZERO)
    check_inverse(operator(edge_phases, 2, ZERO), zero_root)
    receipt.update(exact_matrix_entries=exact_entries, signed_stride_checks=signed_checks,
                   zero_stride_cases=zero_cases, multicycle_cases=multicycle_cases,
                   zero_root_edge_check=True, rounded_cases=rounded_cases,
                   rounded_coordinates=rounded_coordinates,
                   rounded_transcript_sha256=transcript.hexdigest(),
                   maximum_squared_error_to_budget=str(max_ratio),
                   maximum_ratio_case=max_ratio_case, controls=controls(module))
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=HERE.parents[1])
    ap.add_argument('--out', type=Path)
    ap.add_argument('--check', type=Path)
    ap.add_argument('--oracle-only', action='store_true', help='development mode; NOT the full audit')
    args = ap.parse_args()
    require(sys.version_info >= (3, 9), 'Python 3.9+ required')
    if args.oracle_only:
        result = run(None, None)
        result['status'] = 'PASS_ORACLE_ONLY_NOT_PREDECESSOR_REPLAY'
    else:
        source = json.loads((HERE / 'SOURCE.json').read_text())
        with tempfile.TemporaryDirectory(prefix='stride-independent-') as tmp:
            module = load_source(args.repo, source, Path(tmp))
            result = run(module, source)
    raw = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.check:
        require(json.loads(args.check.read_text()) == result, 'complete receipt mismatch')
    if args.out:
        args.out.write_text(raw)
    print(result['status'])
    print(json.dumps(dict(exact_cases=len(result['cases']),
                          all_entry_checks=result['exact_matrix_entries'],
                          rounded_cases=result['rounded_cases'],
                          rounded_coordinates=result['rounded_coordinates'],
                          rejected_controls=len(result['controls'])), sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
