#!/usr/bin/env python3
"""Optional complete five-label local-consistency MILP; floating discovery only.

Apache-2.0; Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def solve(model, seconds, continuous=False):
    import numpy as np
    import scipy
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import coo_array
    saving = .00302177585
    powers = np.array([r ** (1 - saving) for r in range(10)])
    unary = {n: np.zeros(len(d)) for n, d in enumerate(model['domains']) if len(d) > 1}
    pairs = {}

    def add(a, b, ranks, sign):
        table = sign * (powers[np.array(ranks)] - powers[ranks[0][0]])
        if a == b:
            if a in unary:
                unary[a] += table.diagonal()
        elif a not in unary:
            if b in unary:
                unary[b] += table[0]
        elif b not in unary:
            unary[a] += table[:, 0]
        else:
            if a > b:
                a, b, table = b, a, table.T
            if (a, b) not in pairs:
                pairs[a, b] = np.zeros_like(table)
            pairs[a, b] += table

    for _, a, b, r in model['edges']:
        add(a, b, r, 1)
    for _, a, b, r in model['helpers']:
        add(a, b, r, -1)
    # Remove additive row/column terms before allocating pair marginals.
    clean = {}
    for (a, b), table in pairs.items():
        row, col = table[:, 0].copy(), table[0, :].copy()
        unary[a] += row
        unary[b] += col
        table = table - row[:, None] - col[None, :]
        if np.max(np.abs(table)) > 1e-12:
            clean[a, b] = table
    pairs = clean
    offsets, cost = {}, []
    for n, u in unary.items():
        offsets[n] = len(cost)
        cost.extend(u)
    binary_count = len(cost)
    rows, cols, data, rhs = [], [], [], []

    def equality(items, value):
        k = len(rhs)
        rhs.append(value)
        for c, v in items:
            rows.append(k)
            cols.append(c)
            data.append(v)

    for n, u in unary.items():
        equality([(offsets[n] + i, 1) for i in range(len(u))], 1)
    for (a, b), table in pairs.items():
        ma, mb = table.shape
        start = len(cost)
        cost.extend(table.ravel())
        for i in range(ma):
            equality([(start + i * mb + j, 1) for j in range(mb)] +
                     [(offsets[a] + i, -1)], 0)
        # The final column constraint is redundant given the row constraints.
        for j in range(mb - 1):
            equality([(start + i * mb + j, 1) for i in range(ma)] +
                     [(offsets[b] + j, -1)], 0)
    total = len(cost)
    matrix = coo_array((np.array(data), (np.array(rows, dtype=np.int32),
                       np.array(cols, dtype=np.int32))), shape=(len(rhs), total)).tocsc()
    details = dict(variable_contacts=len(unary), binary_labels=binary_count,
                   pair_terms=len(pairs), variables=total, equalities=len(rhs),
                   scipy=scipy.__version__, saving=saving, continuous=continuous)
    print(json.dumps(details), flush=True)
    started = time.monotonic()
    result = milp(np.array(cost) * 1000,
                  integrality=np.r_[np.full(binary_count, 0 if continuous else 1),
                                    np.zeros(total - binary_count)],
                  bounds=Bounds(np.zeros(total), np.ones(total)),
                  constraints=LinearConstraint(matrix, np.array(rhs), np.array(rhs)),
                  options=dict(time_limit=seconds, mip_rel_gap=0.0))
    details.update(status=int(result.status), message=result.message,
                   seconds=time.monotonic() - started)
    if result.fun is not None:
        details['floating_objective'] = float(result.fun / 1000)
    if getattr(result, 'mip_dual_bound', None) is not None:
        details['floating_dual_bound'] = float(result.mip_dual_bound / 1000)
    if result.x is not None:
        fractional = max(abs(float(v) - round(float(v))) for v in result.x[:binary_count])
        details['maximum_label_fractionality'] = fractional
        if fractional < 1e-5:
            assignment = {n: int(np.argmax(result.x[offsets[n]:offsets[n] + len(u)]))
                          for n, u in unary.items()}
            assignment = {n: s for n, s in assignment.items() if s}
            paid, helpers = M.invoice(model, assignment)
            p0, h0 = M.invoice(model, {})
            energy = lambda p, h: sum(count * powers[r] for r, count in p.items()) - sum(
                count * powers[r] for r, count in h.items())
            actual = energy(paid, helpers) - energy(p0, h0)
            M.need(abs(actual - result.fun / 1000) < 1e-6, 'Full invoice equals solver objective')
            details.update(assignment=assignment, paid=dict(paid), helpers=dict(helpers),
                           actual_energy=actual)
    return details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=180)
    ap.add_argument('--continuous', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    M.need(0 < args.seconds <= 180, 'Bounded one-model solve')
    model = M.build()
    print(json.dumps(M.summary(model)), flush=True)
    result = solve(model, args.seconds, args.continuous)
    result['model'] = M.summary(model)
    result['scope'] = 'FLOATING_DISCOVERY_ONLY_NO_SIGNED_NATIVE_OR_KAPPA_ADMISSION'
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'assignment'}), flush=True)


if __name__ == '__main__':
    main()
