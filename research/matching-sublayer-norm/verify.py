"""Source-bound matching-sublayer numerical contract and exact controls."""
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from algebra import cuts, eye, inv, mix_cols, mix_rows, mul, need, norm_cert, op


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'authenticated source bytes: ' + row['path'])
    sys.path.insert(0, str(ROOT / 'research/rational-unitary-fft'))
    from exact import C, Mat
    from engine import Builder, Phases
    source = (ROOT / 'research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py').read_bytes()
    oracle = (ROOT / 'research/cubic-cyclic-inverse/vendor/interval_kernel.py').read_bytes()
    builder = Builder(Phases(10, oracle), 10, source)
    cases = []
    for n in (2, 4):
        plan = builder.namespace['fft'](list(range(n)))
        row = cuts(plan, n, C)
        row.update(label='actual-certified-rational-FFT', n=n)
        cases.append(row)
    builder = Builder(Phases(10, oracle), 10, source)
    plan = builder.plan(Mat([[C(Q(1, 3), Q(1, 5)), C(Q(-1, 4), Q(1, 7))],
                             [C(Q(1, 6), Q(-1, 9)), C(Q(1, 3), Q(1, 5))]]))
    row = cuts(plan, 4, C)
    row.update(label='actual-complete-dirty-Toeplitz-shear', n=4)
    cases.append(row)
    for m in (5, 8, 32):
        p0 = [[C(m), C()], [C(1), C(Q(1, m))]]
        layer = [((0,), [[C(Q(1, m))]]), ((1,), [[C(m)]])]
        plan = [[((0, 1), p0)], layer]
        row = cuts(plan, 2, C)
        row.update(label='sharp-nonunitary-family', m=m)
        cases.append(row)
        h2 = Q((m + 2) ** 2)
        p1 = mul(op(layer, 2, C), p0)
        need(all(norm_cert(x, h2, C) for x in (p0, inv(p0, C), p1, inv(p1, C),
                                              op(layer, 2, C), inv(op(layer, 2, C), C))),
             'common four-way complete-boundary witness envelope')
        partial = mul(op(layer[1:], 2, C), p0)
        need(2 * m * m > h2 and not norm_cert(partial, h2, C),
             'omitting interpolation loss must fail')
        need(norm_cert(partial, 2 * h2, C), 'safe sqrt-two witness bound')
    complex_plan = [[((0, 1), [[C(1, 1), C(3)], [C(1), C(1, -1)]])],
                    [((0,), [[C(2, 1)]]), ((1,), [[C(Q(1, 3), Q(1, 4))]])]]
    row = cuts(complex_plan, 2, C)
    row.update(label='complex-nonunitary-matching', n=2)
    cases.append(row)
    a = [[C(1), C(2)], [C(3), C(5)]]
    b = [[C(2), C(1)], [C(4), C(3)]]
    need(mix_rows(a, b, {0}) != mix_cols(a, b, {0}), 'wrong-side projection control')
    try:
        op([((0,), [[C(2)]]), ((0,), [[C(3)]])], 2, C)
    except ValueError as exc:
        need('matching' in str(exc), 'overlap rejection reason')
    else:
        raise ValueError('overlapping layer must reject')
    need(not norm_cert([[C(0, 2)]], Q(1), C), 'complex adjoint spectral control')
    result = dict(cases=cases, controls=6,
                  source_files=sum(r['usage'] == 'input' for r in sources['files']))
    print(json.dumps(result, sort_keys=True))
    print('PASS_MATCHING_SUBLAYER_NORM four_way_exact_bounds no_new_kappa')


if __name__ == '__main__':
    main()
