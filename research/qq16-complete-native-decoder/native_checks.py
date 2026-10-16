"""Native kernels and full-frame checks adapted verbatim from credited PR2512.
Extended signed line basis check to all112 ports. Source bytes retained.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('complete_native_support',HERE/'native_support.py')
N=importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)
need=N.need
E1=tuple(N.AXES[9:17])

def current_maps(records):
    result = {}
    target = N.phase(N.START)
    for p, rec in records.items():
        g = rec['g']
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(g) for j, b in enumerate(g)), 'actual orthogonal owner matrix')
        b = rec['shift'] ^ rec['inverse_shift']
        need(N.act(g, b) == b, 'current translation is fixed by the involution')
        need(N.phase(N.move_frame(N.START, (g, b))) == target, 'full current frame preserved')
        need(N.phase(N.move_frame(N.START, (g, rec['shift']))) != target, 'old translation is not the current map')
        result[str(p)] = {'owner_columns': list(g), 'translation': b, 'inverse_translation': N.act(g, b)}
    need(len(result) == 104, 'all current map ports')
    return result


def direct_current_frame_checks(records):
    """Independent parity evaluations; no phase-polynomial helper is called."""
    characters = [0] + list(N.AXES) + [a | b for i, a in enumerate(N.AXES) for b in N.AXES[i+1:]]
    checks, rejected = 0, {}
    for p, rec in records.items():
        b = rec['shift'] ^ rec['inverse_shift']
        vectors = rec['g'][:17]
        for w in characters:
            actual = (sum((w & v).bit_count() % 2 for v in vectors) + 2*((w & b).bit_count() % 2)) % 4
            expected = sum((w & e).bit_count() % 2 for e in N.AXES[:17]) % 4
            need(actual == expected, 'independent current-frame character check')
            checks += 1
        difference = b ^ rec['shift']
        w = difference & -difference
        actual = (sum((w & v).bit_count() % 2 for v in vectors) + 2*((w & rec['shift']).bit_count() % 2)) % 4
        expected = sum((w & e).bit_count() % 2 for e in N.AXES[:17]) % 4
        need(w and actual != expected, 'actual old-translation failure witness')
        rejected[str(p)] = {'character': w, 'old_phase': actual, 'required_phase': expected}
    need(checks == 281008, 'all zero/single/pair character checks')
    return {'independent_character_comparisons': checks, 'old_translation_witnesses': rejected}


def gaussian_multiply(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def native_kernels(records):
    lines = 0
    for p in range(112):
        q = records[p]['q']
        for sign in (-1, 1):
            recipe = N.line_recipe(q, sign)
            for address in range(512):
                need(N.kernel(recipe, address) == {address: (1, sign), address ^ q: (1, -sign)}, 'rank-one wrapper kernel')
                lines += 1
    # Embed canonical axes 0..7 into E1=9..16, leaving all other axes as
    # spectators. The wrapper is an involutive coordinate permutation.
    permutation = list(N.AXES)
    for j in range(8):
        permutation[j], permutation[j+9] = permutation[j+9], permutation[j]
    need(N.multiply(tuple(permutation), tuple(permutation)) == N.AXES, 'rank-eight inverse wrapper')
    shift = sum(E1)
    coefficients = 0
    for source in range(256):
        for destination in range(256):
            difference = source ^ destination
            actual = (1, 0)
            expected = (1, 0)
            for j in range(8):
                # Positive F8 followed by translation of all eight axes.
                bit = ((difference ^ 255) >> j) & 1
                actual = gaussian_multiply(actual, (1, -1) if bit else (1, 1))
                bit = (difference >> j) & 1
                expected = gaussian_multiply(expected, (1, 1) if bit else (1, -1))
            need(actual == expected, 'inverse rank-eight Gaussian coefficient')
            coefficients += 1
    need(gaussian_multiply((1, 1), (1, 1)) != gaussian_multiply((1, -1), (1, -1)), 'native inverse sign control')
    return {'rank_one_basis_columns': lines, 'rank_eight_matrix_coefficients': coefficients,
            'rank_eight_wrapper_columns': permutation, 'rank_eight_left_translation': shift,
            'rank_eight_denominator': 256}
