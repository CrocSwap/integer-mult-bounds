"""Exploratory exact group-algebra probe for the QQ16 A/T shear."""
from __future__ import annotations

from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/joint-query"))
import source_data  # noqa: E402
import verify_native  # noqa: E402

A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
AXES = tuple(1 << i for i in range(73))
ID = AXES


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def add(x, y, scale=F(1)):
    out = x.copy()
    for g, c in y.items():
        v = out.get(g, F(0)) + scale * c
        if v:
            out[g] = v
        else:
            out.pop(g, None)
    return out


def scaled(x, c):
    return {g: c * v for g, v in x.items() if c * v}


@lru_cache(None)
def gm(g, h):
    return verify_native.product((g, 0), (h, 0))[0]


@lru_cache(None)
def gi(g):
    return verify_native.inverse((g, 0))[0]


def left(g, x):
    out = {}
    for h, c in x.items():
        gh = gm(g, h)
        out[gh] = out.get(gh, F(0)) + c
    return {k: v for k, v in out.items() if v}


def coeff(x, r):
    return scaled(x, r)


def query(R, routes, stage, values, ports):
    out = [{} for _ in range(8)]
    for p in ports:
        v = values[p]
        if not v:
            continue
        routed = left(routes[p][stage], v)
        for i in range(8):
            c = R[i].get(p, F(0))
            if c:
                out[i] = add(out[i], routed, c)
    return out


def query_adjoint(R, routes, stage, q, ports):
    out = [{} for _ in range(112)]
    for p in ports:
        rg = gi(routes[p][stage])
        v = {}
        for i in range(8):
            c = R[i].get(p, F(0))
            if c:
                v = add(v, q[i], c)
        out[p] = left(rg, v)
    return out


def section(R, routes, stage, q, ports):
    """D_stage^-1 iota_ports R_ports^-1 q, using R_ports^-1=R_ports^T/4."""
    out = [{} for _ in range(112)]
    for p in ports:
        v = {}
        for i in range(8):
            c = R[i].get(p, F(0)) / 4
            if c:
                v = add(v, q[i], c)
        out[p] = left(gi(routes[p][stage]), v)
    return out


def selected_query(R, routes, stage, values, ports):
    return query(R, routes, stage, values, ports)


def identity_columns(values, ports):
    return [[values[p].get(ID, F(0)) for p in ports]]


def family_rank(families, ports):
    """Rank of columns in a sparse Q-vector space keyed by (port, owner map)."""
    basis = {}
    for family in families:
        v = {(p, g): c for p in ports for g, c in family[p].items() if c}
        while v:
            pivot = min(v, key=repr)
            if pivot not in basis:
                scale = v[pivot]
                basis[pivot] = {k: c / scale for k, c in v.items()}
                break
            scale = v[pivot]
            for key, c in basis[pivot].items():
                z = v.get(key, F(0)) - scale * c
                if z:
                    v[key] = z
                else:
                    v.pop(key, None)
    return len(basis)


def det(M):
    a = [list(row) for row in M]
    n = len(a)
    result, sign = F(1), 1
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            sign = -sign
        value = a[j][j]
        result *= value
        for i in range(j + 1, n):
            factor = a[i][j] / value
            for k in range(j + 1, n):
                a[i][k] -= factor * a[j][k]
    return sign * result


def minor_certificate(families, ports):
    """Find eight exact output coordinates with a nonsingular witness matrix."""
    pivots, selected = [], []
    for p in ports:
        maps = sorted({g for family in families for g in family[p]})
        for g in maps:
            row = [family[p].get(g, F(0)) for family in families]
            raw = row[:]
            for pivot, normalized in pivots:
                factor = row[pivot]
                if factor:
                    row = [x - factor*y for x, y in zip(row, normalized)]
            pivot = next((j for j, value in enumerate(row) if value), None)
            if pivot is None:
                continue
            scale = row[pivot]
            pivots.append((pivot, [x / scale for x in row]))
            selected.append({
                "port": p,
                "owner_map_columns_hex": [hex(x) for x in g],
                "coefficients": [str(x) for x in raw],
            })
            if len(pivots) == 8:
                matrix = [[F(value) for value in item["coefficients"]]
                          for item in selected]
                return selected, str(det(matrix))
    return selected, str(F(0))


def main():
    d = source_data.reconstruct(ROOT)
    R = d["R"]
    phases = d["phases"]
    routes = []
    for p, record in enumerate(phases["recipes"]):
        b = tuple([record["q"]] + record["idle_children"][0]["orthogonal_axes"][:8]) + AXES[9:]
        stages = []
        for s in range(3):
            if s == 0:
                actual = AXES
            else:
                swaps = [b[i+1] ^ AXES[9+8*(s-1)+i] for i in range(8)]
                actual = tuple(v ^ verify_native.act(
                    swaps, sum(((v & axis).bit_count() % 2) << i
                               for i, axis in enumerate(swaps))) for v in AXES)
            stages.append(actual)
        routes.append(stages)

    source_witness_images = []
    old_t_outputs = []
    new_t_outputs = []
    for k in range(8):
        e = [{ID: F(i == k)} for i in range(8)]
        b2star = query_adjoint(R, routes, 2, e, U)
        b1b2 = query(R, routes, 1, b2star, U)
        b1starb1b2 = query_adjoint(R, routes, 1, b1b2, U)
        h = [add(scaled(b2star[p], 48), b1starb1b2[p], -1) for p in range(112)]
        need(query(R, routes, 1, h, U) == [{} for _ in range(8)], "B1 h_k is not zero")
        b2h = query(R, routes, 2, h, U)
        need([v.get(ID, F(0)) for v in b2h] == [F(2112 * (i == k)) for i in range(8)],
             "B2 h_k identity coefficient differs from the pinned witness")
        a = section(R, routes, 2, b2h, A)

        # The reviewed post-F0 state: X_U=Y_U=h; X_A=a, Y_A=-a; X_T=Y_T=0.
        x, y = [v.copy() for v in h], [v.copy() for v in h]
        for j, p in enumerate(A):
            x[p], y[p] = a[p].copy(), scaled(a[p], -1)
        for p in T:
            x[p], y[p] = {}, {}

        def b1_t_output(xx, yy):
            # E_2 y = y + P_(2,A)(R_2 - ell_(2,A)) y.
            r2y = query(R, routes, 2, yy, range(112))
            l2ay = query(R, routes, 2, yy, A)
            u = [v.copy() for v in yy]
            correction = section(R, routes, 2,
                                 [add(v, w, -1) for v, w in zip(r2y, l2ay)], A)
            u = [add(v, w) for v, w in zip(u, correction)]
            aa = selected_query(R, routes, 1, xx, T)
            bb = query(R, routes, 1, u, range(112))
            return section(R, routes, 1,
                           [add(v, w, 12) for v, w in zip(bb, aa)], T)

        old = b1_t_output(x, y)
        need(all(not old[p] for p in T), "Zero-shear negative control did not retain the erased T output")
        old_t_outputs.append(old)

        # Sum-preserving A-to-T shear: x_T += x_A and y_T -= x_A.
        for j, (pa, pt) in enumerate(zip(A, T)):
            x[pt] = add(x[pt], x[pa])
            y[pt] = add(y[pt], x[pa], -1)
        new = b1_t_output(x, y)
        new_t_outputs.append(new)
        source_witness_images.append(a)

    source_rank = family_rank(source_witness_images, A)
    output_rank = family_rank(new_t_outputs, T)
    zero_rank = family_rank(old_t_outputs, T)
    need(source_rank == 8, "The post-F0 A witness family is not full rank")
    need(output_rank == 8, "The shear did not reveal eight independent T outputs")
    need(zero_rank == 0, "The zero-shear control should retain the erased output")
    minor_rows, minor_det = minor_certificate(new_t_outputs, T)
    need(len(minor_rows) == 8 and F(minor_det) != 0,
         "The exact post-B1 output minor is singular")
    result = {
        "status": "PASS_QQ16_F0_B1_IDENTITY_SHEAR_WITNESS",
        "scope": "Exact payload-constant regular-cover group algebra on the eight pinned h_k witnesses; one identity-coordinate shear between F0 and B1; not a full controller or supplier.",
        "witness_checks": {
            "B1_h_zero_for_all_eight": True,
            "B2h_identity_coefficient": "2112*I8",
            "post_F0_A_family_rank": source_rank,
        },
        "control": {"zero_shear_post_B1_T_rank": zero_rank},
        "result": {
            "post_B1_T_family_rank": output_rank,
            "distinct_owner_maps_in_T_output": len({g for col in new_t_outputs for p in T for g in col[p]}),
            "nonsingular_minor_determinant": minor_det,
            "minor_rows": minor_rows,
        },
        "local_cost": {
            "selected_additions_per_owner": 16,
            "new_helpers": 0,
            "new_recursive_children": 0,
            "new_coefficients_or_precision": 0,
            "selected_sum_preserved": True,
            "frame_boundary": "F0 output and B1 input share the completed(0) data frame",
        },
        "no_claim": "No complete-controller, recursive supplier, or kappa improvement is established.",
    }
    (Path(__file__).resolve().parent / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("source_A_rank=8; zero_shear_T_rank=0; sheared_post_B1_T_rank=8")
    print("exact_nonzero_8x8_minor_det=" + minor_det)


if __name__ == "__main__":
    main()
