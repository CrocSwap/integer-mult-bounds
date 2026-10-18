#!/usr/bin/env python3
"""Independent review checks for PR1731's two new outer constructions (no new kappa).

Standard library only; imports no PR1731, PR1673 or repository code. Inputs are the exact
PR1731 ledger values vendored in PR1731-INPUTS.json (with source hashes at head 0666300e).

  A. Radix-distributed union schedule (UNION-SCHEDULE.md), re-implemented at operator level
     from its written description and compared exactly with the Kronecker product on random
     instances in the dense-window regime; key lemma, volume identity and negative controls.
  B. Rectangular batching bookkeeping: tau_eff = omega(1,1,5) - 4 and the cited-bound checks.
  C. Exact re-derivation of the balance (epsilon, xi, beta) and kappa from the stated rows,
     the nine row savings, the deleted sparse-fraction row and the old union row.
  D. The T74 supplier moment at 1e-64 resolution with decimal enclosures (220 digits).

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import argparse
import decimal
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
import random

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

PKG = Path(__file__).resolve().parent
INP = json.loads((PKG / "PR1731-INPUTS.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- A. union schedule
def kron_apply(x, T, shape):
    """Theta = (x)_i T_i applied by successive mode products (the definition, no classes)."""
    g = len(shape)
    y = dict(x)
    for i in range(g):
        z = {}
        for idx in itertools.product(*[range(n) for n in shape]):
            z[idx] = sum(T[i][idx[i]][k] * y[idx[:i] + (k,) + idx[i + 1:]] for k in range(shape[i]))
        y = z
    return y


def schedule_apply(x, T, E, shape, order="smallest", drop_round=None, truncate_line=False):
    """UNION-SCHEDULE.md section 2 at operator level: rounds r = 1..R; in round r every record of
    S_r = {|F| >= r} receives T_f along axis f = f_r(F(x)), applied to complete E_f-lines."""
    g = len(shape)
    F = {idx: tuple(i for i in range(g) if idx[i] in E[i]) for idx in x}
    y = dict(x)
    R = max(len(f) for f in F.values())
    stats = {"streamed": 0}
    for r in range(1, R + 1):
        S = [idx for idx in y if len(F[idx]) >= r]
        stats["streamed"] += len(S)
        if r == drop_round:
            continue
        tag = {idx: (F[idx][r - 1] if order == "smallest" else F[idx][-r]) for idx in S}
        Sset = set(S)
        done = set()
        new = dict(y)
        for idx in S:
            f = tag[idx]
            line_key = (f, idx[:f] + idx[f + 1:])
            if line_key in done:
                continue
            done.add(line_key)
            pts = [idx[:f] + (v,) + idx[f + 1:] for v in sorted(E[f])]
            # key lemma: the whole E_f-line is in S_r with the same tag
            assert all(p in Sset and tag[p] == f for p in pts), "incomplete line"
            if truncate_line:
                pts = pts[:-1]
            for p in pts:
                new[p] = sum(T[f][p[f]][q[f]] * y[q] for q in pts)
        y = new
    return y, stats, F


def random_instance(rng, g, L, leak=False, E=None):
    shape = (L,) * g
    if E is None:
        E = [set(rng.sample(range(L), rng.randint(1, L - 1))) for _ in range(g)]
    T = []
    for i in range(g):
        M = [[int(a == b) for b in range(L)] for a in range(L)]
        for a in E[i]:
            for b in E[i]:
                M[a][b] = rng.randint(-3, 3) + (a == b) * 5
        if leak:
            a = rng.choice(sorted(E[i]))
            b = rng.choice(sorted(set(range(L)) - E[i]))
            M[a][b] = 1          # E_i^c -> E_i coupling: violates T_i = I (+) T_i|E_i
        T.append(M)
    x = {idx: rng.randint(-9, 9) for idx in itertools.product(*[range(L)] * g)}
    return shape, E, T, x


def check_union_schedule():
    rng = random.Random(1731)
    cases = 0
    for g, L in [(2, 4), (2, 6), (3, 4), (3, 5), (4, 4)]:
        for _ in range(6):
            shape, E, T, x = random_instance(rng, g, L)
            want = kron_apply(x, T, shape)
            got, st, F = schedule_apply(x, T, E, shape)
            assert got == want, "schedule differs from the Kronecker product"
            got2, _, _ = schedule_apply(x, T, E, shape, order="largest")
            assert got2 == want, "commutation: any per-class axis order must agree"
            flags = sum(len(f) for f in F.values())
            ui = sum(sum(1 for idx in x if idx[i] in E[i]) for i in range(g))
            union = sum(1 for f in F.values() if f)
            assert st["streamed"] == flags == ui <= g * union, "volume identity"
            cases += 1
    # dense-window regime (g * mu > 1): expected flags per record above one
    shape, E, T, x = random_instance(random.Random(7), 4, 4, E=[set(range(1, 4))] * 4)
    want = kron_apply(x, T, shape)
    assert schedule_apply(x, T, E, shape)[0] == want
    controls = {}
    shape, E, T, x = random_instance(random.Random(11), 3, 5, leak=True)
    controls["leaky_T_not_block_diagonal"] = schedule_apply(x, T, E, shape)[0] != kron_apply(x, T, shape)
    shape, E, T, x = random_instance(random.Random(12), 3, 5, E=[set(range(1, 5))] * 3)
    want = kron_apply(x, T, shape)
    assert schedule_apply(x, T, E, shape)[0] == want, "dense control instance must pass unmodified"
    want = kron_apply(x, T, shape)
    controls["skipped_round_2"] = schedule_apply(x, T, E, shape, drop_round=2)[0] != want
    controls["truncated_line"] = schedule_apply(x, T, E, shape, truncate_line=True)[0] != want
    assert all(controls.values()), controls
    return {"random_instances": cases, "dense_regime_instance": "g=4, L=4, |E_i|=3 (expected flags 3 per record)",
            "negative_controls_rejected": sorted(controls)}


# ---------------------------------------------------------------- B, C. arithmetic
def balance():
    c_ = INP["constants_from_check_ledger"]
    led = {k: Q(v) for k, v in INP["ledger_row"].items()}
    r0, zeta, slack, gap = Q(1, 10 ** 64), Q(1, 10 ** 66), Q(1, 10 ** 64), Q(1, 10 ** 64)
    floor_grid, backoff = 10 ** 100, Q(1, 10 ** 76)
    sigma_pub, sigma, k = Q("6.156708"), Q("6.1567081"), 5
    # B: rectangular bookkeeping. A batch: one <W,W,W^k> product per W*W^k right-hand-side entries.
    # Per axis (V W / B entries): (V W/B) / W^(k+1) * W^sigma = (V/B) W^(sigma-k); matching (V/B) W^(tau-1):
    tau_eff = sigma - k + 1
    assert tau_eff == sigma - 4 == Q("2.1567081")
    assert sigma > sigma_pub and sigma > k + 1 and 2 < tau_eff < Q(5, 2)
    # C: rows (savings) from the written constructions; balance main = Gaussian = boundary - slack.
    b = Q(INP["b"])
    q = b - gap
    a = (q + b) / 2
    assert q == led["q"] and a == led["a"]
    c = (3 - tau_eff) / 2                       # boundary saving c + xi - eps  (W = p^(1/2), B = p^xi)
    eps = (1 + q + q * (c - slack - r0 - zeta)) / (1 + q) ** 2
    xi = eps * (1 + q) - c + slack
    beta = 1 - xi - r0 - zeta
    assert (eps, xi, beta) == (led["epsilon"], led["xi"], led["beta"]), "balance not reproduced"
    saving = eps * q
    kappa = Q((saving * floor_grid).__floor__(), floor_grid) - backoff
    assert kappa == led["kappa"], "kappa not reproduced"
    rows = {
        "main_transform": eps * q,
        "fused_gaussian": 1 - eps + q * beta,
        "boundary_algebra": c + xi - eps,
        "group_bit_router": 1 - eps + a * beta,
        "global_coordinate_router": a,
        "group_scans": 1 - eps + beta,
        "sparse_union_movement_new": xi + Q(1, 2) - eps,
        "polynomial_products": eps,
        "core_face_corrections": 1 - (eps + beta - 3),
    }
    assert rows["main_transform"] == rows["fused_gaussian"] and rows["boundary_algebra"] == saving + slack
    assert all(v > kappa for v in rows.values())
    old_union = 1 - eps - beta - Q(1, 2) + xi
    sparse_fraction_exponent = xi - beta - Q(1, 2)
    assert old_union < 0 and sparse_fraction_exponent < 0
    return dict(tau_eff=str(tau_eff), epsilon=float(eps), xi=float(xi), beta=float(beta),
                kappa=str(kappa), kappa_decimal=f"{float(kappa):.18f}",
                row_savings={k_: f"{float(v):.12f}" for k_, v in rows.items()},
                binding_rows=sorted(k_ for k_, v in rows.items() if v - saving < Q(1, 10 ** 30)),
                old_g_factor_union_row=f"{float(old_union):.6f}",
                deleted_sparse_union_fraction_exponent=f"{float(sparse_fraction_exponent):.6f}")


# ---------------------------------------------------------------- D. supplier moment
def moment_enclosure(a, profile, m, W, digits=220):
    """Enclosure of f(a) - 1, f(a) = sum_r n_r r (m/r)^a / (m W), from correctly rounded decimal ln/exp.

    Every operation runs in one local context of `digits` significant digits; each ln/exp result
    (correctly rounded, error <= 1/2 ulp) and each product/sum is widened outward by a relative
    10^-(digits-8), which dominates all roundings of this short computation.
    """
    with decimal.localcontext() as ctx:
        ctx.prec = digits
        D = decimal.Decimal
        ulp = D(10) ** (-(digits - 8))
        A = D(a.numerator) / D(a.denominator)
        lo = hi = D(0)
        for r, n in sorted(profile.items()):
            e = (A * (D(m) / D(r)).ln()).exp()
            w = D(n * r) / D(m * W)
            lo += w * e * (1 - ulp)
            hi += w * e * (1 + ulp)
        return lo * (1 - ulp) - 1, hi * (1 + ulp) - 1


def supplier_moment():
    prof = {int(r): int(n) for r, n in INP["profile"].items()}
    m, W = INP["m"], INP["live"]
    b, above = Q(INP["b"]), Q(INP["b_above_endpoint"])
    lo, hi = moment_enclosure(b, prof, m, W)
    alo, ahi = moment_enclosure(above, prof, m, W)
    assert hi < 0 < alo, "moment must accept b and reject b_above"
    mass = sum(r * n for r, n in prof.items())
    return dict(mass=mass, deficit=m * W - mass, residual_at_b_upper=f"{float(hi):.4e}",
                residual_above_lower=f"{float(alo):.4e}", resolution=str(above - b))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    out = {"union_schedule": check_union_schedule(), "balance": balance(), "supplier_moment": supplier_moment()}
    out["status"] = "PASS_PR1731_UNION_RECT_REVIEW"
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    target = PKG / "RESULT.json"
    if args.write:
        target.write_text(text, encoding="utf-8", newline="\n")
    else:
        assert target.read_text(encoding="utf-8") == text, "RESULT.json differs"
    print(f"{out['status']} schedule_instances={out['union_schedule']['random_instances']} "
          f"kappa={out['balance']['kappa_decimal']} supplier_moment_resolution=1e-64x2 no_new_kappa")


if __name__ == "__main__":
    main()
