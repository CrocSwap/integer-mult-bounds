"""Derive the rational dual certificates (needs numpy and scipy; not registered).

Solves the symmetry-reduced Shannon-type linear program for each graph, rounds
the dual to rationals and keeps it only if the exact check in star_graphs
accepts it.  The registered verifier never imports this file.
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import star_graphs as sg  # noqa: E402

GRAPHS = {
    "wheel-W4": (5, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (4, 1)]),
    "K33": (6, [(a, b) for a in range(3) for b in range(3, 6)]),
}
# Not certified: the float optimum is 7.0 but the rounded dual is rejected by the
# exact check, so the prism is solved only when named on the command line.
UNCERTIFIED = {
    "prism": (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
}
MAX_DENOMINATOR = 10 ** 6


def orbit_representatives(nbrs, group):
    """Map every closed set to the least member of its orbit."""
    total = len(nbrs)
    closure = [sg.close(mask, nbrs) for mask in range(1 << total)]
    rep = {}
    for mask in sorted(set(closure)):
        if mask not in rep:
            orbit = {sg.image(perm, mask) for perm in group}
            least = min(orbit)
            for member in orbit:
                rep[member] = least
    return closure, rep


def reduced_rows(nbrs, closure, rep):
    """Distinct orbit-space rows of the M and S inequalities."""
    total = len(nbrs)
    identity = list(range(total))
    rows = {}
    for base in sorted(set(rep.values())):
        free = [v for v in range(total) if not (base >> v) & 1]
        entries = [["M", base, v] for v in free]
        entries += [["S", base, i, j] for i in free for j in free if i < j]
        for entry in entries:
            terms, constant = sg.certificate_terms(entry, identity)
            row = {}
            for mask, sign in terms:
                key = rep[closure[mask]]
                row[key] = row.get(key, 0) + sign
            row = {key: value for key, value in row.items() if value}
            if row:
                rows.setdefault((tuple(sorted(row.items())), constant), entry)
    return rows


def solve(n, edges):
    """Return (float optimum, rational certificate) for one graph."""
    nbrs = sg.neighbour_masks(n, edges)
    total = len(nbrs)
    group = sg.vertex_permutations(n, edges)
    closure, rep = orbit_representatives(nbrs, group)
    rows = reduced_rows(nbrs, closure, rep)
    column = {mask: i for i, mask in enumerate(sorted(set(rep.values())))}
    keys = list(rows)
    r_idx, c_idx, data = [], [], []
    for r, (items, _) in enumerate(keys):
        for mask, value in items:
            r_idx.append(r)
            c_idx.append(column[mask])
            data.append(-value)
    a_ub = coo_matrix((data, (r_idx, c_idx)), shape=(len(keys), len(column))).tocsr()
    b_ub = np.array([-constant for _, constant in keys], float)
    cost = np.zeros(len(column))
    cost[column[rep[closure[0]]]] = 1
    a_eq = coo_matrix(([1.0], ([0], [column[(1 << total) - 1]])), shape=(1, len(column))).tocsr()
    result = linprog(cost, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=[total],
                     bounds=(None, None), method="highs-ds")
    sg.require(result.status == 0, result.message)
    duals = -result.ineqlin.marginals
    certificate = []
    for r, key in enumerate(keys):
        if duals[r] > 1e-10:
            weight = Fraction(float(duals[r])).limit_denominator(MAX_DENOMINATOR)
            certificate.append([rows[key], str(weight)])
    return float(result.fun), certificate


def main(out_path, names):
    records = []
    for name in names:
        n, edges = {**GRAPHS, **UNCERTIFIED}[name]
        value, certificate = solve(n, edges)
        bound = sg.certified_bound(n, edges, certificate)
        print(name, "float optimum", value, "exact bound", bound, "entries", len(certificate))
        records.append({"name": name, "points": n, "edges": [list(e) for e in edges],
                        "lower_bound": str(bound), "certificate": certificate})
    Path(out_path).write_text(json.dumps({"schema_version": 1, "graphs": records},
                                         separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or list(GRAPHS))
