# SPDX-License-Identifier: Apache-2.0
"""Exact differential checks and failure controls for the opt-in R420 adapter."""
import copy
import argparse
import gzip
import hashlib
import itertools
import json
import random
import subprocess
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter as A


def canonical(value):
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, (tuple, list)):
        return [canonical(x) for x in value]
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    return value


def digest(value):
    return hashlib.sha256(json.dumps(canonical(value), sort_keys=True).encode()).hexdigest()


def matrices():
    # Exhaustive binary matrices through 3x3, including rectangular/empty shapes.
    yield []
    for height in range(1, 4):
        for width in range(4):
            for entries in itertools.product((0, 1), repeat=height * width):
                yield [list(entries[r * width:(r + 1) * width]) for r in range(height)]
    # Negative pivots, a required swap, skipped columns and genuinely rational RREF.
    yield [[0, -2, 3], [0, 4, -6]]
    yield [[0, 0, 1], [0, -3, 2]]
    yield [[2, 1, 1], [0, 3, 1]]
    yield [[Fraction(1, 3), Fraction(2, 7)], [Fraction(2, 3), Fraction(4, 7)]]
    rng = random.Random(94)
    for case in range(400):
        height, width = rng.randrange(1, 17), rng.randrange(13)
        rows = [[Fraction(rng.randrange(-31, 32), rng.randrange(1, 32))
                 for _ in range(width)] for _ in range(height)]
        if case % 2 == 0 and height > 1:
            rows[-1] = [(-3) * x for x in rows[0]]
        if case % 5 == 0:
            rows[0] = [x * (2 ** 257) for x in rows[0]]
        if case % 7 == 0:
            rows[0] = [Fraction(0) for _ in rows[0]]
        yield rows


def call(engine, suite):
    result = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'worker.py'), engine, suite],
                            capture_output=True, check=True)
    A.require(not result.stderr, 'Unexpected worker stderr')
    return result.stdout


def outcome(checker, word):
    try:
        _, labels, replay, hypotheses, conclusion, info = checker.check(word)
    except checker.Reject as error:
        return {'reject': str(error)}
    return {'labels': labels, 'replay': replay, 'hypotheses': hypotheses,
            'conclusion': conclusion, 'interleaving': info}


def verify():
    reference, integer = A.load_checker(False), A.load_checker(True)
    with gzip.open(A.WORD, 'rt') as source:
        word = json.load(source)
    frame_results = []
    for frame in word['frames']:
        rows = [word['lines'][i] for i in frame]
        before = copy.deepcopy(rows)
        left, right = reference.rref(rows), integer.rref(rows)
        A.require(left == right and rows == before, 'Frame RREF/pivot mismatch or input mutation')
        ns = reference.nullspace_int(rows)
        A.require(ns == integer.nullspace_int(rows), 'Integer annihilator basis changed')
        A.require(len(ns) == 8 - len(left[1]), 'Rank/nullity mismatch')
        A.require(all(sum(x*y for x, y in zip(row, n)) == 0 for row in rows for n in ns),
                  'Annihilator dot product is not zero')
        frame_results.append((left, ns))
    cases = list(matrices())
    algebra_results = []
    for rows in cases:
        before = copy.deepcopy(rows)
        left, right = reference.rref(rows), integer.rref(rows)
        A.require(left == right and rows == before, 'Supplemental RREF mismatch or mutation')
        A.require(all(isinstance(x, Fraction) for row in right[0] for x in row), 'RREF type changed')
        algebra_results.append(right)
    # Actual broken arithmetic implementations, not just altered expected receipts.
    source = (HERE / 'vendor/exact_rows.py').read_text()
    changes = {
        'omit_back_elimination': ('targets = range(len(rows)) if reduced else range(rank + 1, len(rows))',
                                  'targets = range(rank + 1, len(rows))'),
        'wrong_elimination_sign': ('a*x - b*y', 'a*x + b*y'),
        'skip_first_column': ('for column in range(len(rows[0])):',
                              'for column in range(1, len(rows[0])):'),
    }
    detected = {}
    original_kernel = A._kernel
    try:
        for name, (old, new) in changes.items():
            A.require(source.count(old) == 1, 'Mutation no longer matches the pinned kernel')
            broken = types.ModuleType(name)
            exec(compile(source.replace(old, new), name, 'exec'), broken.__dict__)
            A._kernel = broken
            for index, rows in enumerate(cases):
                if A.rref(rows) != algebra_results[index]:
                    detected[name] = {'case': index, 'matrix': canonical(rows)}
                    break
            A.require(name in detected, 'Arithmetic mutant survived: ' + name)
    finally:
        A._kernel = original_kernel
    # Fraction truncation must be noticed on a non-integral RREF, independently of pivot checks.
    nonintegral = [[2, 1, 1], [0, 3, 1]]
    basis, pivots = A.rref(nonintegral)
    A.require(([[Fraction(int(x)) for x in row] for row in basis], pivots)
              != reference.rref(nonintegral), 'Fraction-truncation control is vacuous')
    detected['truncate_final_fractions'] = {'matrix': nonintegral}

    # Changed geometry is recomputed on each call, without cache admission.
    geometries = {}
    full = next(i for i, f in enumerate(word['frames']) if len(f) == 120)
    variants = {}
    bad = copy.deepcopy(word); bad['lines'][0] = list(bad['lines'][1]); variants['duplicate_label'] = bad
    bad = copy.deepcopy(word); bad['lines'][0] = [0]*8; variants['zero_label'] = bad
    bad = copy.deepcopy(word); bad['lines'][0] = [2*x for x in bad['lines'][0]]; variants['scaled_label'] = bad
    bad = copy.deepcopy(word); bad['frames'][full].pop(); variants['unclosed_full_frame'] = bad
    bad = copy.deepcopy(word); bad['frames'][full].append(120); variants['out_of_range_line'] = bad
    for name, changed in variants.items():
        left, right = outcome(reference, changed), outcome(integer, changed)
        A.require(left == right and 'reject' in left, 'Geometry rejection mismatch: ' + name)
        geometries[name] = left
    # A nontrivial valid relabelling must pass too (orthogonal signed coordinate permutation).
    reflected = copy.deepcopy(word)
    reflected['lines'] = [[-r[7]] + r[:7] for r in reflected['lines']]
    left, right = outcome(reference, reflected), outcome(integer, reflected)
    A.require(left == right and 'reject' not in left and all(left['hypotheses'].values())
              and all(left['conclusion'].values()), 'Reflected/permuted valid geometry failed')

    source_controls = []
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='r420 source controls ') as temp:
        root = Path(temp)
        for row in manifest['files']:
            target = root / row['path']; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((A.ROOT / row['path']).read_bytes())
        A.bind_sources(root)
        for row in manifest['files']:
            path = root / row['path']; data = path.read_bytes(); path.write_bytes(data + b' ')
            try:
                A.bind_sources(root)
            except ValueError as error:
                A.require(str(error).startswith('Source pin mismatch:'), 'Wrong pin rejection')
                source_controls.append(row['path'])
            else:
                raise ValueError('Changed source accepted')
            finally:
                path.write_bytes(data)
    optimized = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'worker.py'),
                                'integer', 'controls'], capture_output=True)
    A.require(optimized.returncode != 0 and b'Assertions must remain enabled' in optimized.stderr,
              'Optimized-Python refusal failed')
    check_ref, check_int = call('reference', 'check'), call('integer', 'check')
    A.require(check_ref == check_int, 'Complete-check receipts differ')
    controls_ref, controls_int = call('reference', 'controls'), call('integer', 'controls')
    A.require(controls_ref == controls_int and b'9/9 negative controls rejected, 1/1 positive control accepted' in controls_int,
              'Original mutation controls/diagnostics differ')
    check_summary = json.loads(check_ref)
    del check_summary['dimensions'], check_summary['annihilators']
    return dict(status='PASS_R420_RREF_PERFORMANCE', seed=94, frames=len(frame_results),
                supplemental_matrices=len(cases), frame_results_sha256=digest(frame_results),
                algebra_results_sha256=digest(algebra_results), kernel_mutations=detected,
                geometry_rejections=geometries, valid_geometry_control='signed coordinate permutation',
                source_controls=source_controls, optimized_python_refused=True,
                original_controls={'negative': 9, 'positive': 1},
                complete_check_sha256=hashlib.sha256(check_ref).hexdigest(),
                controls_sha256=hashlib.sha256(controls_ref).hexdigest(),
                complete_check=check_summary, controls_stdout=controls_ref.decode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Optional fresh path for the complete verification receipt')
    args = parser.parse_args()
    A.require(args.out is None or not args.out.exists(), 'Output path must be fresh')
    result = verify()
    expected_path = HERE / 'EXPECTED.json'
    A.require(result == json.loads(expected_path.read_text()), 'Committed verification receipt changed')
    if args.out:
        with args.out.open('x') as output:
            json.dump(result, output, indent=2, sort_keys=True); output.write('\n')
    print(result['status'], 'frames=' + str(result['frames']),
          'matrices=' + str(result['supplemental_matrices']), 'original_controls=9+1 kernel_mutations=4')
