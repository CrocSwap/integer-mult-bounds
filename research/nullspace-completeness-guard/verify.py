#!/usr/bin/env python3
"""Source-bound nullspace guard; ywz65, Apache-2.0, OpenAI Codex assistance."""
import argparse
import ast
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from guard import PRIMES, certify, guarded_kernel, require


def authenticate():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for item in sources['files']:
        if item['usage'] == 'input':
            require(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
                    == item['sha256'], 'changed source: ' + item['path'])
    snapshots = json.loads((HERE / 'SNAPSHOTS.json').read_text(encoding='utf-8'))
    for item in snapshots['files']:
        require(hashlib.sha256((HERE / item['snapshot']).read_bytes()).hexdigest()
                == item['sha256'], 'changed snapshot: ' + item['snapshot'])


def load_candidate():
    source = (HERE / 'snapshots/pr2537-verify.py').read_text(encoding='utf-8')
    nodes = [n for n in ast.parse(source).body
             if isinstance(n, ast.FunctionDef) and n.name == 'null_exact_ff']
    require(len(nodes) == 1, 'one source kernel required')
    namespace = {'gcd': math.gcd}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'pinned-pr2537-kernel', 'exec'), namespace)
    return namespace['null_exact_ff']


def determinant(a):
    if not a:
        return 1
    return sum((-1)**j * x * determinant([r[:j] + r[j+1:] for r in a[1:]])
               for j, x in enumerate(a[0]))


def minor_rank(a, n):
    # Independent tiny-matrix oracle: determinants, no Gaussian elimination.
    for size in range(min(len(a), n), 0, -1):
        for rs in itertools.combinations(range(len(a)), size):
            for cs in itertools.combinations(range(n), size):
                if determinant([[a[i][j] for j in cs] for i in rs]):
                    return size
    return 0


def rejected(fn, fragment):
    try:
        fn()
    except ValueError as exc:
        require(fragment in str(exc), 'unexpected rejection: ' + str(exc))
        return
    raise ValueError('negative control accepted: ' + fragment)


def controls(candidate):
    for p in PRIMES:
        require(p > 1 and all(p % d for d in range(2, math.isqrt(p)+1)), 'nonprime modulus')
    checked = guarded_kernel(candidate)
    cases = 0
    for m in range(3):
        for n in range(4):
            for flat in itertools.product((-1, 0, 1), repeat=m*n):
                a = [list(flat[i*n:(i+1)*n]) for i in range(m)]
                b = checked(a, n)
                require(len(b) == n - minor_rank(a, n), 'independent minor nullity')
                require(minor_rank(b, n) == len(b), 'independent minor basis rank')
                if b:
                    certify(a, n, [[-3*x for x in row] for row in reversed(b)])
                cases += 1
    a, b = [[1, 0, 0]], [[0, 1, 0], [0, 0, 1]]
    rejected(lambda: certify(a, 3, b[:-1]), 'incomplete')
    rejected(lambda: certify(a, 3, [b[0], b[0]]), 'dependent')
    rejected(lambda: certify(a, 3, [b[0], [0, 0, 0]]), 'dependent')
    rejected(lambda: certify(a, 3, [b[0], [1, 0, 1]]), 'annihilation')
    rejected(lambda: certify(a, 3, [[0, 1]]), 'rectangular')
    rejected(lambda: certify(a, 3, [[False, 1, 0]]), 'rectangular')
    rejected(lambda: certify(a, 3, [[0.0, 1, 0]]), 'rectangular')
    rejected(lambda: certify([], -1, []), 'dimension')
    rejected(lambda: certify([], True, []), 'dimension')
    rejected(lambda: certify([], 1, [[1], [1]]), 'too many')
    def mutate_input(matrix, n):
        matrix[0][:] = [0] * n
        return [[int(i == j) for j in range(n)] for i in range(n)]
    rejected(lambda: guarded_kernel(mutate_input)(a, 3), 'annihilation')
    outside = [0, 0, 1]
    require(all(sum(x*y for x, y in zip(outside, row)) == 0 for row in b[:-1]),
            'dropped-vector permissiveness fixture')
    require(not all(sum(x*y for x, y in zip(outside, row)) == 0 for row in b),
            'complete basis must reject outside vector')
    q = math.prod(PRIMES)
    require(certify([[q, 0]], 2, [[0, 1]])['input'] == 'exact', 'input fallback')
    require(certify([], 2, [[q, q], [q, -q]])['basis'] == 'exact', 'basis fallback')
    require(certify([], 2, [[1, 1], [1, -1]])['basis'] == 'modular', 'basis modular route')
    return {'exhaustive_integer_matrices': cases, 'negative_controls': 11,
            'unlucky_prime_fallbacks': 2, 'noncanonical_bases_accepted': True,
            'dropped_vector_makes_old_test_permissive': True}


def census(candidate):
    require(not sys.flags.optimize, 'actual inherited assertions require nonoptimized Python')
    sys.path[:0] = [str(ROOT / 'research/bit-reuse-147'), str(ROOT / 'scripts'),
                    str(ROOT / 'references/partial-gauge/pr97')]
    import word147
    import frames147
    import linalg
    import check_lifted
    counts, digest, concrete = Counter(), hashlib.sha256(), []
    def checked(matrix, n):
        a = [list(row) for row in matrix]
        b = candidate([row[:] for row in a], n)
        witness = certify(a, n, b)
        counts['calls'] += 1
        counts['input_' + witness['input']] += 1
        counts['basis_' + witness['basis']] += 1
        digest.update(json.dumps([a, n, b], separators=(',', ':')).encode())
        if not concrete and len(b) >= 2:
            concrete.append((a, n, b))
        return b
    previous = linalg.null_exact, check_lifted.null_exact
    linalg.null_exact = check_lifted.null_exact = checked
    try:
        _, w, _, schedule, _, folder = word147.load_schedule()
        exact = frames147.Exact(schedule, w, folder)
    finally:
        linalg.null_exact, check_lifted.null_exact = previous
    require(concrete, 'actual nontrivial basis fixture')
    a, n, b = concrete[0]
    rejected(lambda: certify(a, n, b[:-1]), 'incomplete')
    rejected(lambda: certify(a, n, b[:-1] + [b[0]]), 'dependent')
    return {'ambient_dimension': exact.h, 'calls': dict(sorted(counts.items())),
            'ordered_input_output_sha256': digest.hexdigest(),
            'actual_basis_deletion_and_duplication_rejected': True,
            'scope': 'Complete Exact initializer only; no fresh/all move or scalar replay'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls-only', action='store_true')
    parser.add_argument('--write', action='store_true', help='explicit receipt regeneration')
    args = parser.parse_args()
    authenticate()  # Before parsing or executing external source.
    candidate = load_candidate()
    result = {'controls': controls(candidate)}
    if not args.controls_only:
        result['initializer'] = census(candidate)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        require(not args.controls_only, 'cannot replace full receipt with controls only')
        (HERE / 'RESULT.json').write_text(encoded, encoding='utf-8', newline='\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        if args.controls_only:
            expected = {'controls': expected['controls']}
        require(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True),
                'typed receipt mismatch')
    print(json.dumps(result, sort_keys=True))
    print('PASS_NULLSPACE_COMPLETENESS_GUARD' + ('_CONTROLS_ONLY' if args.controls_only else ''))


if __name__ == '__main__':
    main()
