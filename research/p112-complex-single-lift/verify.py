"""Exact regression evidence for the support-preserving complex-to-real lift.

Python 3.10+, standard library, Apache-2.0. Prepared for @woklerx with
substantial OpenAI Codex assistance. The all-complex theorem is in PROOF.md;
these finite tests are not a formal proof of it or of integer multiplication.
"""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = '407d52ff15b2217b6e22bce44728b4c3907b6515'
SEED = 40
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def c(re=0, im=0):
    return F(re), F(im)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def scale(a, r):
    return a[0]*r, a[1]*r


def inv(a):
    norm = a[0]*a[0] + a[1]*a[1]
    require(norm != 0, 'division by zero complex value')
    return a[0]/norm, -a[1]/norm


def csum(values):
    re, im = F(0), F(0)
    for a, b in values:
        re, im = re + a, im + b
    return re, im


def readers(x, a):
    return [csum(scale(value, scalar) for scalar, value in zip(row, a))
            for row in x]


def exclusion_set(x, a, z):
    """Nonzero values whose real projection must stay nonzero (PROOF.md)."""
    values = list(a) + readers(x, a)
    for row, value in zip(x, z):
        if value != ZERO:
            reciprocal = inv(value)
            values.append(reciprocal)
            values.extend(sub(aj, scale(reciprocal, scalar))
                          for aj, scalar in zip(a, row))
    return set(values) - {ZERO}


def project(x, a, z, forced_t=None):
    exclusions = exclusion_set(x, a, z)
    forbidden = {-re/im for re, im in exclusions if im}
    t = next(k for k in range(len(exclusions) + 1) if k not in forbidden)
    if forced_t is not None:
        t = forced_t
    require(all(re + t*im for re, im in exclusions), 'projection hits an excluded zero')
    projected_a = [re + t*im for re, im in a]
    projected_z = []
    for value in z:
        if value == ZERO:
            projected_z.append(F(0))
        else:
            re, im = inv(value)
            projected_z.append(1/(re + t*im))
    return projected_a, projected_z, t, len(exclusions)


def terms(x, a, z):
    result = []
    for j, aj in enumerate(a):
        result.append(([c(row[j]) for row in x],
                       [sub(c(row[j]), mul(aj, zi)) for row, zi in zip(x, z)]))
    result.append((readers(x, a), z))
    return result


def support(value):
    return tuple(i for i, entry in enumerate(value) if entry != ZERO)


def supports(word):
    return [(support(d), support(s)) for d, s in word]


def identity(word, x):
    for i in range(len(x)):
        for j in range(len(x)):
            actual = csum(mul(d[i], s[j]) for d, s in word)
            expected = c(sum(a*b for a, b in zip(x[i], x[j])))
            if actual != expected:
                return False
    return True


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def check_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    require(manifest['base_commit'] == BASE, 'base commit mismatch')
    for name, expected in manifest['inputs_sha256'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                'source hash mismatch: ' + name)


def load_geometry():
    spec = importlib.util.spec_from_file_location(
        'p112_predecessor_geometry', ROOT / 'research/p112-single-lift/geometry.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.build()
    module.check_geometry(data)
    return module, data


def diagnostic_cases(x):
    rng = random.Random(SEED)
    # Covers every active size, unequal magnitudes/phases, and sources outside col(X).
    for k in range(9):
        a = [c((-1)**j*(j+1), (j % 3)+1) if j < k else ZERO for j in range(8)]
        z = [c(F(rng.randrange(-3, 4), 3), F(rng.randrange(-3, 4), 5))
             for _ in x]
        yield 'active_' + str(k), a, z
    for name, a in [
        ('common_phase', [scale(c(1, 2), (-1)**j) for j in range(8)]),
        ('distinct_phases', [c(j+1, 8-j) for j in range(8)]),
    ]:
        z = [scale(inv(a[i % 8]), row[i % 8]) for i, row in enumerate(x)]
        yield name, a, z
    a = [c(1, 1), c(0, 1)] + [ZERO]*6
    yield 'single_port_source', a, [c(2, -1) if i == SEED else ZERO for i in range(len(x))]
    yield 'sharp_zero_source', [c(1, 1)]*8, [ZERO]*len(x)
    yield 'sharp_singleton', [c(1, 1)] + [ZERO]*7, [scale(inv(c(1, 1)), row[0]) for row in x]


def controls():
    rejected = []

    def reject(name, action):
        try:
            action()
        except (ValueError, ZeroDivisionError):
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    # The residual exclusion is essential to EQUALITY, not just monotonicity.
    x, a, z = [[1]], [c(1, 1)], [ONE]
    reject('omitted_residual_exclusion', lambda: project(x, a, z, forced_t=0))
    require(supports(terms(x, a, z)) != supports(terms(x, [ONE], [ONE])),
            'control must actually lose a residual nonzero')
    reject('omitted_inverse_exclusion', lambda: project([[1]], [ONE], [c(0, 1)], forced_t=0))
    reject('omitted_reader_exclusion', lambda: project([[1, 1]], [c(1, 1), c(-1, 1)], [ZERO], forced_t=0))
    reject('omitted_coefficient_exclusion', lambda: project([[0]], [c(0, 1)], [ZERO], forced_t=0))
    word = terms(x, a, z)
    require(identity(word, x), 'bilinear identity positive control')
    reject('conjugated_sources', lambda: require(identity([(d, [(re, -im) for re, im in s])
                                                          for d, s in word], x), 'adjoint is not transpose'))
    reject('omitted_ninth_term', lambda: require(identity(word[:-1], x), 'missing term'))
    bad = [(d, list(s)) for d, s in word]
    bad[0][1][0] = add(bad[0][1][0], ONE)
    reject('corrupted_compensation', lambda: require(identity(bad, x), 'bad compensation'))
    # f applied directly to z is incorrect: the inverse projection is necessary.
    x2, a2, z2 = [[1]], [c(1, 1)], [inv(c(1, 1))]
    old = supports(terms(x2, a2, z2))
    reject('project_z_directly', lambda: require(old == supports(terms(x2, [ONE], [c(F(1, 2))])),
                                                 'direct projection loses cancellation'))
    return rejected


def run():
    check_sources()
    geometry, data = load_geometry()
    x = data['X']
    records = []
    for name, a, z in diagnostic_cases(x):
        ar, zr, t, count = project(x, a, z)
        old, new = terms(x, a, z), terms(x, [c(v) for v in ar], [c(v) for v in zr])
        require(supports(old) == supports(new), 'support mismatch: ' + name)
        require(support(a) == support([c(v) for v in ar]), 'coefficient support mismatch')
        old_cost = [geometry.term_cost([v != ZERO for v in d], [v != ZERO for v in s], data)
                    for d, s in old]
        new_cost = [geometry.term_cost([v != ZERO for v in d], [v != ZERO for v in s], data)
                    for d, s in new]
        require(old_cost == new_cost and sum(old_cost) >= 64, 'cost mismatch: ' + name)
        full_matrix = name in ('common_phase', 'distinct_phases', 'sharp_singleton')
        if full_matrix:
            require(identity(old, x) and identity(new, x), 'bilinear identity: ' + name)
        # Check exact per-entry compensation identities in every diagnostic.
        for i, row in enumerate(x):
            for j, aj in enumerate(a):
                require(add(old[j][1][i], mul(aj, z[i])) == c(row[j]), 'complex compensation')
                require(new[j][1][i][0] + ar[j]*zr[i] == row[j], 'real compensation')
        records.append({'name': name, 'active': len(support(a)), 't': t,
                        'nonzero_exclusions': count, 'term_costs': old_cost,
                        'support_sha256': digest(supports(old)), 'full_matrix_check': full_matrix})
    require(records[-1]['term_costs'] == [0] + [8]*8, 'nonzero sharp ninth term')
    # The transfer lemma is not restricted to the P112 alphabet or shape.
    general_x = [[F(1, 2), -2, 3], [4, 0, F(1, 3)]]
    general_a = [c(1, 1), c(F(2, 3), -1), c(0, 2)]
    general_z = [scale(inv(general_a[0]), general_x[0][0]),
                 scale(inv(general_a[2]), general_x[1][2])]
    ar, zr, t, count = project(general_x, general_a, general_z)
    old = terms(general_x, general_a, general_z)
    new = terms(general_x, [c(v) for v in ar], [c(v) for v in zr])
    require(old[0][1][0] == old[2][1][1] == ZERO, 'rational coordinate cancellations')
    require(supports(old) == supports(new), 'general rectangular support transfer')
    require(identity(old, general_x) and identity(new, general_x), 'general rectangular identity')
    return {'schema': 1, 'base_commit': BASE, 'assignment_seed': SEED,
            'diagnostics': records, 'negative_controls': controls(),
            'general_real_matrix_control': {'shape': [2, 3], 't': t, 'nonzero_exclusions': count},
            'scalar_domain': 'exact Gaussian rationals in diagnostics; all complex values in written proof',
            'conclusion': 'every complex single lift has a real lift with identical term supports and copy costs'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path, default=HERE / 'RESULTS.json')
    args = parser.parse_args()
    # Re-establish the inherited finite premises; never trust its saved PASS alone.
    check_sources()
    flags = ['-O'] if not __debug__ else []
    subprocess.run([sys.executable, *flags, '-S', '-B', str(ROOT / 'research/p112-single-lift/verify.py')], check=True)
    subprocess.run([sys.executable, *flags, '-S', '-B', str(ROOT / 'research/p112-single-lift/independent_check.py')], check=True)
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        require(result == json.loads(args.check.read_text(encoding='utf-8')), 'certificate mismatch')
    subprocess.run([sys.executable, *flags, '-I', '-S', '-B', str(HERE / 'independent_check.py'),
                    '--check', str(HERE / 'INDEPENDENT.json')], check=True)
    print('PASS_P112_COMPLEX_SINGLE_LIFT: 14 exact projections; 8 negative controls; identical term costs; floor 64')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print('FAIL_P112_COMPLEX_SINGLE_LIFT: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
