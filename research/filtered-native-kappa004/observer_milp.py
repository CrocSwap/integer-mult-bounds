#!/usr/bin/env python3
"""Discovery MILP for joint decoding of noisy lower-frame observations.

Coefficients are bounded only for this search. A positive selected set is
rechecked over Q; neither a solver failure nor its bound is a theorem here.
Apache-2.0; OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import time
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from snapshot_probe import Span

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', type=int, default=0)
    ap.add_argument('--seconds', type=int, default=90)
    ap.add_argument('--maximum-cost', type=int, default=8)
    args = ap.parse_args()
    begin = time.monotonic()
    path = HERE/'evidence/observer-subspaces.json.gz'
    data = json.loads(gzip.decompress(path.read_bytes()))
    target = {int(i): Q(a) for i, a in data['targets'][args.mode]}
    frames, columns = [], []
    # Explicit positive control: a ground RY gather followed by one H9.
    # It is excluded by an eight-rank budget and admitted at nine.
    if args.maximum_cost >= 9:
        frames.append({'frame': 0, 'rank': 0, 'cost': 9})
        columns.append((0, target, {'frame': 0, 'owner': 'ground_RY_mode',
                                    'mode': args.mode, 'after_event': -1}))
    for item in data['frames']:
        price = 9-item['rank']
        if price > args.maximum_cost:
            continue
        basis = Span()
        for record in item['rows']:
            basis.insert({int(i): Q(a) for i, a in record['row']}, record['description'])
        if not basis.columns:
            continue
        f = len(frames)
        frames.append({'frame': item['frame'], 'rank': item['rank'], 'cost': price})
        for row, desc in basis.columns:
            columns.append((f, row, desc))
    coords = sorted(set(target) | {i for _, row, _ in columns for i in row})
    ci = {i: k for k, i in enumerate(coords)}
    n, nf, nc = len(columns), len(frames), len(coords)
    rr, cc, vv = [], [], []
    limit = 32.
    lower, upper = [float(target.get(i, 0)) for i in coords], [float(target.get(i, 0)) for i in coords]
    for j, (f, row, _) in enumerate(columns):
        for i, a in row.items():
            rr.append(ci[i]); cc.append(j); vv.append(float(a))
        for sign in (1, -1):
            rownum = len(lower)
            rr += [rownum, rownum]; cc += [j, n+f]; vv += [sign, -limit]
            lower.append(-np.inf); upper.append(0.)
    rownum = len(lower)
    for f, item in enumerate(frames):
        rr.append(rownum); cc.append(n+f); vv.append(item['cost'])
    lower.append(-np.inf); upper.append(args.maximum_cost)
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(lower), n+nf)).tocsc()
    objective = np.array([0.]*n+[float(f['cost']) for f in frames])
    integrality = np.array([0]*n+[1]*nf)
    print('MILP', args.mode, n, nf, nc, 'budget',args.maximum_cost,flush=True)
    result = milp(objective, integrality=integrality,
                  bounds=Bounds([-limit]*n+[0.]*nf, [limit]*n+[1.]*nf),
                  constraints=LinearConstraint(matrix, lower, upper),
                  options={'time_limit': args.seconds, 'mip_rel_gap': .0001})
    selected = []
    residual = None
    recipe = None
    if result.x is not None:
        active = {f for f in range(nf) if result.x[n+f] > .5}
        selected = [frames[f] for f in sorted(active)]
        basis = Span()
        for f, row, desc in columns:
            if f in active:
                basis.insert(row, desc)
        rem, rep = basis.solve(target)
        residual = len(rem)
        if not rem:
            recipe = [{'coefficient': str(a), **basis.columns[j][1]} for j, a in rep.items()]
    out = {'status': 'BOUNDED_COEFFICIENT_NOISY_OBSERVER_MILP', 'mode': args.mode,
           'input_sha256': sha256(path.read_bytes()).hexdigest(),
           'maximum_lift_rank_cost': args.maximum_cost, 'coefficient_bound': limit,
           'continuous_columns': n, 'frame_variables': nf, 'coordinates': nc,
           'solver_status': int(result.status), 'solver_message': result.message,
           'solver_objective': None if result.fun is None else float(result.fun),
           'solver_lower_bound': None if getattr(result, 'mip_dual_bound', None) is None else float(result.mip_dual_bound),
           'selected_frames': selected, 'rational_residual_terms': residual,
           'rational_recipe': recipe,
           'scope': 'Necessary fixed-vector quotient; bounded numerical coefficient search. Rational reconstruction verifies only a selected set in that quotient. A full phase-aware physical repair and every cost remain required.',
           'new_kappa_claimed': False, 'elapsed_seconds': time.monotonic()-begin}
    (HERE/f'evidence/observer-milp-mode{args.mode}-budget{args.maximum_cost}.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'rational_recipe'}), flush=True)


if __name__ == '__main__':
    main()
