"""Meaningful arithmetic/contract controls for the grouped construction."""
from fractions import Fraction as F
from pathlib import Path
import json

from gaussian import G, rounded, solve, solve_dyadic
from grouped import compose, exact_mixed, group
from weighted import constants, require

P = Path(__file__).resolve().parent


def main():
    rejected = []
    def reject(name, function):
        try:
            function()
        except (ValueError, ZeroDivisionError) as error:
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError('control accepted: '+name)

    inside = ([G(F(3, 8), F(1, 4))]*3, [F(1, 2)]*3)
    outside = ([G(F(-1, 2)), G(F(1, 4), F(1, 4))], [F(1, 2)]*2)
    phases = [G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13)), G(0, 1), G(1)]
    u = F(1, 1 << 64)
    x0 = [G(F(i-3, 4)+u, F(2*i-3, 8)-u) for i in range(4)]
    y0 = [G(F(i+19, 8)-u, F(3-i, 4)+u) for i in range(4)]
    z0 = [G(F(-13+2*i, 4)+u, F(-13-3*i, 8)-u) for i in range(4)]
    def run(mutation=None):
        x, y, z = x0.copy(), y0.copy(), z0.copy()
        stats, bound = compose(x, y, z, inside, outside, phases, 1, 7, 64, mutation=mutation)
        return x, y, z, stats, bound
    x, y, z, stats, bound = run()
    want = exact_mixed(x0, inside[0], outside[0], phases, 1, 7)
    for mutation in ['wrong_inner_shift', 'coarse_window', 'coarse_gauge', 'coarse_multiplier']:
        mx, my, mz, _, _ = run(mutation)
        require(any((a-b-c).norm2() > bound**2 for a, b, c in zip(my, y0, want)),
                'deliberate mathematical defect not detected: '+mutation)
        rejected.append(dict(name=mutation, reason='original mixed-operator error bound exceeded'))
    # Wrong signed order still restores x/z, but does not invert the word.
    for name, sign in [('B', -1), ('A', -1), ('B', 1), ('A', 1)]:
        if name == 'B':
            group(x, z, outside[0], outside[1], False, phases, 1, 7, 64, sign)
        else:
            group(z, y, inside[0], inside[1], True, phases, 1, 1, 64, sign)
    require(x == x0 and z == z0 and y != y0, 'wrong inverse-order control')
    rejected.append(dict(name='wrong_inverse_order', reason='target does not cancel although dirty arrays restore'))
    reject('source_target_alias', lambda: compose(x0, x0, z0, inside, outside, phases, 1, 7, 64))
    reject('connector_source_alias', lambda: compose(x0, y0, x0, inside, outside, phases, 1, 7, 64))
    reject('bad_direction', lambda: compose(x0.copy(), y0.copy(), z0.copy(), inside, outside, phases, 0, 7, 64))
    reject('bad_sign', lambda: compose(x0.copy(), y0.copy(), z0.copy(), inside, outside, phases, 1, 7, 64, 0))
    reject('nonunit_phase', lambda: compose(x0.copy(), y0.copy(), z0.copy(), inside, outside,
                                          [G(2)]+phases[1:], 1, 7, 64))
    reject('off_grid', lambda: compose([G(F(1, 3))]+x0[1:], y0.copy(), z0.copy(), inside, outside, phases, 1, 7, 64))
    reject('unstable_root', lambda: constants([G(1)], [F(1)]))
    reject('false_radius', lambda: constants([G(F(3, 4))], [F(1, 2)]))
    reject('zero_outside_reciprocal', lambda: group(x0.copy(), y0.copy(), [G()], [F(0)], False, phases, 1, 1, 64))
    reject('nondyadic_solver_input', lambda: solve_dyadic([[G(F(1, 3))]], [G(1)]))
    reject('singular_solver', lambda: solve_dyadic([[G()]], [G(1)]))

    solver_rows = []
    for n in range(1, 9):
        for shift in range(n):
            # Permuted diagonal matrices force row pivots, including zero
            # real diagonals from imaginary factors. The dense upper part
            # and dyadic scalings give nontrivial exact divisions.
            a = [[G() for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    a[(i+shift) % n][j] = G(F(0 if i == j else i+j+1, 1 << (i+1)),
                                            F(2*i+1 if i == j else j-i, 1 << (j+1)))
            b = [G(F(i-3, 8), F(2*i+1, 16)) for i in range(n)]
            audit = {}
            out = solve_dyadic(a, b, audit)
            require(out == solve(a, b), 'independent Gaussian-rational solve')
            require(all(sum((v*w for v, w in zip(row, out)), G()) == rhs for row, rhs in zip(a, b)),
                    'independent exact solve residual')
            dim = 2*n
            require(audit['maximum_minor_bits'] <= dim*(audit['input_bits']+(dim-1).bit_length())+1,
                    'integer minor size bound')
            solver_rows.append(dict(complex_dimension=n, permutation=shift, **audit))
    require(any(row['row_pivots'] for row in solver_rows), 'nonvacuous solver row pivots')
    require(rounded(G(F(1, 2), F(-1, 2)), 0) == G(1, 0), 'signed half ties')
    result = dict(status='PASS', rejected=rejected, solvers=solver_rows, signed_rounding_ties=True)
    print('PASS', len(rejected), 'negative controls;', len(solver_rows), 'independent fraction-free solves')
    return result


if __name__ == '__main__':
    main()
