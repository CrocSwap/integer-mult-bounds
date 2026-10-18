#!/usr/bin/env python3
"""Nominate exact symbolic LP duals for every component (discovery only; uses highspy/scipy).

The verifier (verify.py) uses only the standard library and the shipped rational duals.
"""
import argparse, gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
import highspy
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import splu
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as Mo
from engine import adjusted_bounds


def solve_component(comp, cnum):
    cols, rhs = comp['cols'], comp['rhs']; nr, nc = len(rhs), len(cols)
    cost = np.array([sum(v * cnum[k] for k, v in enumerate(col[1])) for col in cols])
    starts = [0]; idx = []; val = []
    for col in cols:
        for r, a in col[2]: idx.append(r); val.append(float(a))
        starts.append(len(idx))
    lp = highspy.HighsLp(); lp.num_col_ = nc; lp.num_row_ = nr
    lp.col_cost_ = cost; lp.col_lower_ = np.zeros(nc); lp.col_upper_ = np.full(nc, highspy.kHighsInf)
    lp.row_lower_ = np.array(rhs, float); lp.row_upper_ = np.array(rhs, float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise; lp.a_matrix_.start_ = np.array(starts, np.int32)
    lp.a_matrix_.index_ = np.array(idx, np.int32); lp.a_matrix_.value_ = np.array(val)
    h = highspy.Highs(); h.setOptionValue('output_flag', False); h.setOptionValue('primal_feasibility_tolerance', 1e-10)
    h.setOptionValue('dual_feasibility_tolerance', 1e-10); h.passModel(lp); h.run()
    assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal
    b = h.getBasis(); basic_cols = [j for j in range(nc) if b.col_status[j] == highspy.HighsBasisStatus.kBasic]
    basic_rows = [i for i in range(nr) if b.row_status[i] == highspy.HighsBasisStatus.kBasic]
    assert len(basic_cols) + len(basic_rows) == nr
    # Equations on q: A_j^T q = c_j for basic columns j; q_i = 0 for basic (redundant) rows i.
    R = []; C = []; V = []; eq = 0
    for j in basic_cols:
        for r, a in cols[j][2]: R.append(eq); C.append(r); V.append(float(a))
        eq += 1
    for i in basic_rows: R.append(eq); C.append(i); V.append(1.0); eq += 1
    Msys = csc_matrix((V, (R, C)), shape=(nr, nr)); lu = splu(Msys)
    duals = []
    for k in range(8):
        rhs_k = np.array([float(cols[j][1][k]) for j in basic_cols] + [0.0] * len(basic_rows))
        duals.append(lu.solve(rhs_k))
    D = [[Q(float(duals[k][i])).limit_denominator(10 ** 6) for k in range(8)] for i in range(nr)]
    return D, h.getInfo().objective_function_value


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); out = {}
    lower, upper = adjusted_bounds()
    cnum = [float((lower[k] + upper[k]) / 2) for k in range(2, 10)]
    for word in ('jp8', 'ck'):
        for prog in ('forward', 'backward'):
            c, ev = Mo.load(a.work / (word + '-local'), prog)
            F, nodes, climbs, center = Mo.extract(c, ev); lo, hi = Mo.intervals(c, F, nodes)
            comps, const, base, free = Mo.lp(c, F, nodes, lo, hi)
            certs = []
            for comp in comps:
                D, val = solve_component(comp, cnum)
                certs.append([[str(x) for x in row] for row in D])
            out['%s/%s' % (word, prog)] = certs
            print(word, prog, 'components', len(comps), 'rows', sum(len(x['rhs']) for x in comps), flush=True)
    a.out.write_bytes(gzip.compress(json.dumps(out, separators=(',', ':'), sort_keys=True).encode(), mtime=0))
