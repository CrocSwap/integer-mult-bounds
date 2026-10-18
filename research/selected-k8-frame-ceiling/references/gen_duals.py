"""Nominate symbolic exact duals for every component (solver side; not part of the proof).

Needs numpy, scipy and highspy. HiGHS solves each component's LP at the excluded
exponent; its optimal basis is then inverted for each rank coordinate C_2..C_9
separately, so every dual entry is a rational linear form in those charges. The
rational values are checked exactly here and again, independently of any solver,
by verify.py. Output: data/DUALS.json.gz (deterministic).
"""
import argparse
import gzip
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import highspy
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as M          # noqa: E402
import verify as V         # noqa: E402

RANKS = range(2, M.H + 1)


def numeric_charges(b):
    """C_d / (b * 73^b) as floats; only the solver uses these."""
    x = float(b)
    return [0.0, 0.0] + [(d ** (1 - x) - d) / x for d in RANKS]


def solve(rows, rhs, cols, gamma):
    nr, nc = len(rows), len(cols)
    start, index, value = [0], [], []
    cost = []
    for _, c, entries in cols:
        cost.append(sum(c[d] * gamma[d] for d in range(len(c))))
        for i, a in sorted(entries):
            index.append(i)
            value.append(float(a))
        start.append(len(index))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = nc, nr
    lp.col_cost_ = np.array(cost)
    lp.col_lower_ = np.zeros(nc)
    lp.col_upper_ = np.full(nc, highspy.kHighsInf)
    lp.row_lower_ = np.array(rhs, dtype=float)
    lp.row_upper_ = np.array(rhs, dtype=float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = np.array(start, dtype=np.int32)
    lp.a_matrix_.index_ = np.array(index, dtype=np.int32)
    lp.a_matrix_.value_ = np.array(value)
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    h.setOptionValue('presolve', 'off')
    h.setOptionValue('solver', 'simplex')
    h.passModel(lp)
    h.run()
    assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal, h.modelStatusToString(h.getModelStatus())
    basis = h.getBasis()
    sol = h.getSolution()
    return h.getInfo().objective_function_value, basis, list(sol.col_value)


def symbolic_duals(rows, cols, basis):
    basic_cols = [j for j in range(len(cols)) if basis.col_status[j] == highspy.HighsBasisStatus.kBasic]
    active_rows = [i for i in range(len(rows)) if basis.row_status[i] != highspy.HighsBasisStatus.kBasic]
    assert len(basic_cols) == len(active_rows), (len(basic_cols), len(active_rows))
    rpos = {i: k for k, i in enumerate(active_rows)}
    data, ri, ci = [], [], []
    for kc, j in enumerate(basic_cols):
        for i, a in cols[j][2]:
            if i in rpos:
                # transpose: row = basic column, column = active row
                ri.append(kc)
                ci.append(rpos[i])
                data.append(float(a))
    At = sp.csc_matrix((data, (ri, ci)), shape=(len(basic_cols), len(active_rows)))
    lu = spla.splu(At)
    q = {}
    for d in RANKS:
        rhs_d = np.array([float(cols[j][1][d]) for j in basic_cols])
        sol = lu.solve(rhs_d)
        for k, i in enumerate(active_rows):
            x = F(float(sol[k])).limit_denominator(1 << 20)
            if x:
                q.setdefault(i, {})[d] = x
    # exact check on the basic columns: A_B^T q == c_B coordinate-wise
    for j in basic_cols:
        key, c, entries = cols[j]
        for d in RANKS:
            s = sum((a * q.get(i, {}).get(d, 0) for i, a in entries), F(0))
            assert s == c[d], ('rationalised dual is not exact on a basic column', key, d, s, c[d])
    return q


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'data' / 'DUALS.json.gz')
    args = parser.parse_args()
    word, src = V.load_selected_word(V.REPO)
    model = M.Model(word)
    b = V.excluded_exponent(V.REPO)
    gamma = numeric_charges(b)
    comps = model.components()
    out = {'excluded_b': f'{b.numerator}/{b.denominator}', 'word_content_sha256': src['content_sha256'],
           'components': []}
    base_total = [0] * (M.H + 1)
    for n, comp in enumerate(comps):
        labels, unary, pairs = model.component_problem(comp)
        rows, rhs, cols = M.lp(labels, unary, pairs)
        base = M.assignment_cost(labels, unary, pairs, {node: model.baseline()[node] for node in comp})
        base_num = sum(base[d] * gamma[d] for d in range(len(base)))
        obj, basis, x = solve(rows, rhs, cols, gamma)
        gap = base_num - obj
        if gap > 1e-7:
            frac = [cols[j][0] for j in range(len(cols)) if 1e-9 < x[j] < 1 - 1e-9]
            print('component', n, 'LP below baseline by', gap, 'fractional columns', len(frac), flush=True)
        q = symbolic_duals(rows, cols, basis)
        dual_obj = [0] * (M.H + 1)
        for i, vec in q.items():
            if rhs[i]:
                for d, x_ in vec.items():
                    dual_obj[d] += x_ * rhs[i]
        neg = 0
        for key, c, entries in cols:
            r = sum((c[d] - sum((a * q.get(i, {}).get(d, 0) for i, a in entries), F(0))) * gamma[d] for d in RANKS)
            if r < -1e-9:
                neg += 1
        same = all(dual_obj[d] == base[d] for d in RANKS)
        print(f'component {n}: nodes={len(comp)} rows={len(rows)} cols={len(cols)} '
              f'lp={obj:.9f} base={base_num:.9f} identity={same} negative_reduced={neg}', flush=True)
        for d in RANKS:
            base_total[d] += base[d]
        out['components'].append({
            'first': json.dumps(comp[0]), 'nodes': len(comp),
            'duals': {json.dumps(rows[i]): {str(d): f'{x_.numerator}/{x_.denominator}' for d, x_ in sorted(vec.items())}
                      for i, vec in sorted(q.items())}})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, sort_keys=True, separators=(',', ':')).encode()
    args.output.write_bytes(gzip.compress(payload, mtime=0))
    print('wrote', args.output, len(payload), 'bytes; components', len(comps))


if __name__ == '__main__':
    main()
