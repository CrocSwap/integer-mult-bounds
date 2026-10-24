#!/usr/bin/env python3
"""Bounded exact calibration; universal claims are proved in PROOF.md.

Apache-2.0; substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import random
import subprocess
import sys
import tempfile

from exact import G, fingerprint, load, need, parse, rowmul, zeros
from certify import certify
from check_certificate import check
from models import (MPO, add, compose, cyclic_delay, difference, identity,
                    local, native_frontend, prefix_xor, recurrence, scale,
                    transpose, unit)

ROOT = Path(__file__).resolve().parent


def literal_entry(data, word, output=0, source=0):
    """Separate path-sum oracle; it does not use the producer's row updates."""
    _, n, _, _, left, right, trans = parse(data)
    total = G()
    for path in product(range(n), repeat=len(word)+1):
        value = left[output][path[0]]*right[path[-1]][source]
        if not value:
            continue
        for j, symbol in enumerate(word):
            value = value*trans[symbol][path[j]][path[j+1]]
            if not value:
                break
        total = total+value
    return total


def entry(a, outputs, inputs):
    v = list(a.left)
    for y, x in zip(outputs, inputs):
        t = a.transitions.get((y, x))
        if t is None:
            return G()
        v = rowmul(v, t)
    return sum((x*y for x, y in zip(v, a.right)), G())


def verified(a, expected):
    data = a.problem() if isinstance(a, MPO) else a
    certificate = certify(data)
    need(certificate['kind'] == expected, 'unexpected decision')
    result = check(data, certificate)
    return data, certificate, result


def core_suite():
    rng = random.Random(20261024)
    differential = 0
    for n in range(1, 4):
        for _ in range(8):
            a = MPO(2, [G(rng.randrange(-1, 2)) for _ in range(n)],
                    [G(rng.randrange(-1, 2)) for _ in range(n)],
                    {(y, x): [[G(rng.randrange(-1, 2)) for _ in range(n)] for _ in range(n)]
                     for y in range(2) for x in range(2)})
            data = a.problem()
            certificate = certify(data)
            check(data, certificate)
            if certificate['kind'] == 'counterexample':
                value = literal_entry(data, certificate['word'])
                from exact import scalar
                need(value == scalar(certificate['value']) and value, 'path-sum discrepancy')
                differential += 1
            else:
                for width in range(1, n+1):
                    for word in product(sorted(data['transitions']), repeat=width):
                        need(not literal_entry(data, word), 'path-sum equality')
                        differential += 1
    # A correct positive-width identity can fail at the empty word.
    empty_only = MPO(1, [G(1)], [G(1)], {(0, 0): [[G()]]})
    verified(empty_only, 'all_positive_widths')
    need(sum((x*y for x, y in zip(empty_only.left, empty_only.right)), G()) == 1,
         'empty-width discriminator')
    # Uniform repeated columns miss a mixed-column defect.
    a, b = zeros(3, 3), zeros(3, 3)
    a[0][1], b[1][2] = G(1), G(1)
    mixed = MPO(2, [G(1), G(), G()], [G(), G(), G(1)], {(0, 0): a, (1, 1): b})
    _, mixed_certificate, _ = verified(mixed, 'counterexample')
    need(len(mixed_certificate['word']) == 2, 'mixed-word witness')
    for width in range(1, 9):
        for bit in range(2):
            need(not entry(mixed, [bit]*width, [bit]*width), 'uniform-column false positive')
    sharp = []
    for n in range(1, 13):
        a = cyclic_delay(n)
        _, c, _ = verified(a, 'counterexample')
        need(len(c['word']) == n, 'positive-width cutoff is sharp')
        for width in range(1, n):
            need(not entry(a, [0]*width, [0]*width), 'delayed first discrepancy')
        sharp.append(n)
    x = local(2, {(0, 1): 1, (1, 0): 1})
    z = local(2, {(0, 0): 1, (1, 1): -1})
    xz = compose(x, z)
    for i in range(2):
        for j in range(2):
            wanted = (-1 if j else 1) if i == 1-j else 0
            need(entry(xz, [i], [j]) == wanted, 'noncommuting composition order')
    verified(difference(compose(x, z), compose(z, x)), 'counterexample')
    w = local(2, {(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): -1})
    wrong = difference(compose(w, w), scale(unit(2), G(2)))
    _, c, _ = verified(wrong, 'counterexample')
    need(len(c['word']) == 2, 'exterior scalar must not be tensor-powered')
    right = recurrence(unit(2), [[G(2)]], [G(1)], [G(1)])
    verified(difference(compose(w, w), right), 'all_positive_widths')
    jordan = [[G(1), G(1)], [G(), G(1)]]
    linear_width = recurrence(unit(2), jordan, [G(1), G()], [G(), G(1)])
    for width in range(1, 10):
        need(entry(linear_width, [0]*width, [0]*width) == width, 'recurrent width coefficient')
    phase = local(2, {(0, 0): G(0, 1), (1, 1): G(0, 1)})
    phase_error = difference(phase, unit(2))
    verified(phase_error, 'counterexample')
    cycle4 = cyclic_delay(4)
    filtered = recurrence(phase_error, cycle4.transitions[0, 0], cycle4.left, cycle4.right)
    verified(filtered, 'all_positive_widths')
    # Infinite-order Q(i) unitary and a nonlinear local permutation.
    alpha = G(Fraction(3, 5), Fraction(4, 5))
    t = local(2, {(0, 0): 1, (1, 1): alpha})
    tinv = local(2, {(0, 0): 1, (1, 1): G(1)/alpha})
    verified(difference(compose(tinv, t), unit(2)), 'all_positive_widths')
    tof = local(8, {(x ^ (4 if x & 3 == 3 else 0), x): 1 for x in range(8)})
    verified(difference(compose(tof, tof), unit(8)), 'all_positive_widths')
    # A defect exclusively on a later borrowed/rectangular channel must be
    # reported; checking only the first demanded block would miss it.
    roles = {'local_dimension': 1, 'states': 1, 'outputs': 2, 'inputs': 3,
             'left': [[0], [1]], 'right': [[0, 0, 1]], 'transitions': {'0,0': [[1]]}}
    _, c, witness = verified(roles, 'counterexample')
    need((c['output'], c['input']) == (1, 2), 'all independent rectangular role channels')
    complete_zero = {'local_dimension': 1, 'states': 2, 'outputs': 2, 'inputs': 3,
                     'left': [[1, 0], [2, 0]], 'right': [[0, 0, 0], [1, 2, 3]],
                     'transitions': {'0,0': [[1, 0], [0, 0]]}}
    verified(complete_zero, 'all_positive_widths')
    return {'path_sum_comparisons': differential, 'random_transducers': 24,
            'sharp_first_failure_widths': sharp, 'mixed_word_width': 2,
            'wrong_Hadamard_scale_failure_width': 2,
            'recurrence_widths': 9, 'phase_filter_period': 4,
            'rectangular_role_controls': 2}


def column_suite():
    p = prefix_xor()
    pinv = transpose(p)
    positive = difference(compose(pinv, p), unit(2))
    data, cert, _ = verified(positive, 'all_positive_widths')
    columns = 0
    for width in range(1, 7):
        for bits in product(range(2), repeat=width):
            total = 0
            out = []
            for x in bits:
                total ^= x
                out.append(total)
            need(entry(p, out, bits) == 1, 'literal prefix action')
            need(entry(pinv, bits, out) == 1, 'literal inverse action')
            columns += 1
    # Every output entry through width four, not just its deterministic image.
    all_entries = 0
    for width in range(1, 5):
        for x in product(range(2), repeat=width):
            y_expected = tuple(sum(x[:j+1]) % 2 for j in range(width))
            for y in product(range(2), repeat=width):
                need(entry(p, y, x) == int(y == y_expected), 'complete prefix matrix')
                all_entries += 1
    # Witness that this is outside sums of identical one-column tensor powers.
    # Swapping two columns and taking prefix XOR do not commute.
    need(entry(p, [1, 1], [1, 0]) == 1 and entry(p, [1, 1], [0, 1]) == 0,
         'column-permutation noncommutation')
    u = ((0, 0), (1, 1))
    v = ((0, 0), (1, 0))
    hankel = [[entry(p, [a[0], b[0]], [a[1], b[1]]) for b in v] for a in u]
    need(hankel == identity(2), 'prefix Hankel minor')
    return {'literal_prefix_columns': columns, 'complete_prefix_entries': all_entries,
            'inverse_certificate_states': data['states'], 'invariant_rows': cert['rank'],
            'exact_minimum_prefix_bond': 2}, data, cert


def routing_suite():
    counts = []
    for k in range(1, 5):
        half = 1 << k
        size = half*half
        # Flatten the half-swap coefficient tensor at the middle cut.
        # Row=(y_left,x_left), column=(y_right,x_right).
        rows, cols = [], []
        for yl in range(half):
            supported = []
            for xl in range(half):
                column = xl*half+yl
                supported.append(column)
                cols.append(column)
                rows.append(yl*half+xl)
                for yr in range(half):
                    for xr in range(half):
                        value = int(yl == xr and yr == xl)
                        need(value == int(yr*half+xr == column), 'half-swap unfolding entry')
            need(len(supported) == half, 'row indexing')
        need(sorted(rows) == list(range(size)) and sorted(cols) == list(range(size)),
             'unfolding is a full permutation matrix')
        # Rank-D column projection has exactly the stated discarded energy.
        for bond in (0, 1, size//2, size):
            discarded_square = sum(1 for j in cols if j >= bond)
            need(discarded_square == size-bond, 'sharp unfolding Frobenius tail')
        counts.append({'width': 2*k, 'unfolding_rank': size, 'entry_checks': size*size})
    walsh = []
    for k in range(1, 7):
        size = 1 << k
        h = [[G(-1 if (a & b).bit_count() % 2 else 1) for b in range(size)]
             for a in range(size)]
        for a in range(size):
            for b in range(size):
                # Integer evaluation is an independent exact Gram oracle.
                inner = sum((-1 if ((a ^ b) & t).bit_count() % 2 else 1)
                            for t in range(size))
                need(inner == (size if a == b else 0), 'paired-phase Walsh Gram')
        for bond in (0, 1, size//2, size):
            discarded = sum(1 for row in h for j in range(bond, size) if row[j])
            need(discarded == size*(size-bond), 'paired-phase discarded energy')
        walsh.append({'width': 2*k, 'cut_rank': size, 'squared_singular_value': size})
    return {'half_swaps': counts, 'paired_quadratic_phases': walsh}


def approximate_cutoff_control():
    # A fixed unitary per instance can pass small-width tolerance checks and
    # still have a large late-width error. All comparisons are exact rationals.
    cases = []
    for n in (16, 64, 128):
        alpha = G(n, 1)/G(n, -1)
        value = G(1)
        for width in range(1, 9):
            value = value*alpha
            error = value-G(1)
            square = error.a*error.a+error.b*error.b
            need(square <= Fraction(4*width*width, n*n), 'short-width unitary tolerance')
        late = 3*n//2
        value = G(1)
        for _ in range(late):
            value = value*alpha
        error = value-G(1)
        need(error.a*error.a+error.b*error.b > 2, 'large late unitary error')
        cases.append({'parameter': n, 'early_widths': 8, 'late_width': late,
                      'late_error_squared_exceeds': 2})
    return cases


def source_suite():
    sources = load(ROOT/'SOURCES.json')
    source_row = next(row for row in sources['files']
                      if row['path'] == 'research/native-tensor-cutoff/examples/source-conjugation.json')
    need(hashlib.sha256((ROOT/'SOURCE-FIXTURE.json').read_bytes()).hexdigest() == source_row['sha256'],
         'portable literal source fixture hash')
    fixture = load(ROOT/'SOURCE-FIXTURE.json')
    blocks = native_frontend(fixture)
    certificates = []
    for i, row in enumerate(blocks):
        for j, block in enumerate(row):
            data, cert, _ = verified(block, 'all_positive_widths')
            certificates.append({'output': i, 'input': j, 'states': data['states'],
                                 'invariant_rows': cert['rank']})
    # Independently enumerate the literal conjugation on all source addresses.
    n = fixture['axes']
    units = (G(1), G(0, 1), G(-1), G(0, -1))

    def literal(recipe, address):
        bits = [(address >> j) & 1 for j in range(n)]
        out = [((recipe['offset'] >> j) & 1) ^
               (sum(bits[k] for k in range(n) if recipe['matrix_rows'][j] >> k & 1) % 2)
               for j in range(n)]
        phase = recipe['phase'] + sum(a*b for a, b in zip(recipe['linear_Z4'], bits))
        for j in range(n):
            for k in range(j+1, n):
                phase += 2*bits[j]*bits[k]*((recipe['quadratic_rows'][j] >> k) & 1)
        return sum(bit << j for j, bit in enumerate(out)), units[phase % 4]

    g, z, r = (fixture['generators'][s] for s in ('G', 'Z', 'R'))
    inverse = {literal(g, x)[0]: (x, G(1)/literal(g, x)[1]) for x in range(1 << n)}
    for x in range(1 << n):
        a, pa = inverse[x]
        b, pb = literal(z, a)
        c, pc = literal(g, b)
        target, phase = literal(r, x)
        need((c, pa*pb*pc) == (target, phase), 'source conjugation all addresses')
    p = prefix_xor(1 << n, 4)
    encoded = compose(transpose(p), compose(blocks[1][0], p))
    data, cert, _ = verified(encoded, 'all_positive_widths')
    changed = deepcopy(fixture)
    changed['generators']['R']['phase'] = 0
    wrong = native_frontend(changed)[1][0]
    _, mutation, _ = verified(wrong, 'counterexample')
    need(len(mutation['word']) == 1, 'source absolute phase mutation')
    return {'source_axes': n, 'source_instruction_count': len(fixture['program']),
            'independent_source_addresses': 1 << n, 'all_owner_blocks': certificates,
            'encoded_source_shear_states': data['states'],
            'encoded_source_invariant_rows': cert['rank'],
            'encoded_source_local_entries': len(data['transitions']),
            'absolute_phase_mutation_width': 1}


def controls(data, certificate):
    rejected = []

    def reject(name, problem, claim):
        try:
            check(problem, claim)
        except (ValueError, ZeroDivisionError):
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)

    c = deepcopy(certificate); c['width_bound'] += 1
    reject('width-bound', data, c)
    c = deepcopy(certificate); del c['seeds'][next(iter(c['seeds']))]
    reject('missing-seed-symbol', data, c)
    c = deepcopy(certificate); del c['closure'][next(iter(c['closure']))]
    reject('missing-closure-symbol', data, c)
    c = deepcopy(certificate)
    symbol = next(iter(c['closure']))
    from exact import scalar
    c['closure'][symbol][0][0] = (scalar(c['closure'][symbol][0][0])+G(1)).json()
    reject('wrong-closure', data, c)
    changed = deepcopy(data)
    nonzero_column = next(j for j in range(data['states']) if any(scalar(v[j]) for v in certificate['basis']))
    changed['right'] = [[int(i == nonzero_column)] for i in range(data['states'])]
    reject('changed-dirty-return-binding', changed, certificate)
    c = deepcopy(certificate); c['problem_sha256'] = fingerprint(changed)
    reject('changed-dirty-return-semantic', changed, c)
    bad = deepcopy(data); bad['left'][0][0] = 0.5
    reject('float-coefficient', bad, certificate)
    bad = deepcopy(data); bad['transitions']['01,0'] = bad['transitions'][next(iter(bad['transitions']))]
    reject('noncanonical-alphabet-entry', bad, certificate)
    _, negative, _ = verified(cyclic_delay(4), 'counterexample')
    c = deepcopy(negative); c['value'] = 0
    reject('zero-counterexample', cyclic_delay(4).problem(), c)
    c = deepcopy(negative); c['word'] = c['word'][:-1]
    reject('wrong-counterexample-width', cyclic_delay(4).problem(), c)
    return rejected


def standalone(data, certificate):
    with tempfile.TemporaryDirectory(prefix='finite-memory-checker-') as folder:
        out = Path(folder)
        for name in ('exact.py', 'check_certificate.py'):
            (out/name).write_bytes((ROOT/name).read_bytes())
        (out/'problem.json').write_text(json.dumps(data))
        (out/'certificate.json').write_text(json.dumps(certificate))
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
        for p in out.iterdir():
            p.chmod(0o444)
        out.chmod(0o555)
        try:
            for optimized in (False, True):
                # Isolated mode excludes the script directory, so this standalone
                # CLI deliberately uses -B and a private empty bytecode prefix.
                args = [sys.executable, '-B', '-X', 'pycache_prefix='+str(out/'absent-cache')]
                if optimized:
                    args.append('-O')
                args += [str(out/'check_certificate.py'), str(out/'problem.json'), str(out/'certificate.json')]
                run = subprocess.run(args, cwd=out, env={'PATH': ''}, capture_output=True, text=True, timeout=30)
                need(run.returncode == 0, 'standalone checker: '+run.stderr[-1000:])
                need(json.loads(run.stdout)['status'] == 'PASS_ALL_POSITIVE_WIDTHS', 'standalone output')
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
            need(before == after, 'standalone bytes/inventory changed')
        finally:
            out.chmod(0o755)
            for p in out.iterdir():
                p.chmod(0o644)
    return 'producer_absent_readonly_empty_PATH_normal_and_optimized'


def source_pins(root):
    sources = load(ROOT/'SOURCES.json')
    for row in sources['files']:
        need(hashlib.sha256((Path(root)/row['path']).read_bytes()).hexdigest() == row['sha256'],
             'source hash: '+row['path'])
    need((Path(root)/'research/native-tensor-cutoff/examples/source-conjugation.json').read_bytes() ==
         (ROOT/'SOURCE-FIXTURE.json').read_bytes(), 'literal source fixture equality')
    return len(sources['files'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('all', 'core'), default='all')
    parser.add_argument('--source-root')
    args = parser.parse_args()
    result = {'status': 'PASS_FINITE_MEMORY_LIFTING_CALIBRATION', 'core': core_suite()}
    if args.suite == 'all':
        result['columns'], data, cert = column_suite()
        result['routing'] = routing_suite()
        result['approximate_cutoff_controls'] = approximate_cutoff_control()
        result['native'] = source_suite()
        result['rejections'] = controls(data, cert)
        result['standalone'] = standalone(data, cert)
    if args.source_root:
        source_pins(args.source_root)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
