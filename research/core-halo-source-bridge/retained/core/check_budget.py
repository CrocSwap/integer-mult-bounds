"""Exact provider-join budget checks and omitted-charge counterexamples.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is a bounded exact observer, not a physical execution or an inference
of the production source regime from tested sizes.
"""
from fractions import Fraction as Q
from hashlib import sha256
from independent_numerics import (
    apply_matrix, budget, canonical_json, dyadic_at_least, five_factors,
    identity, inverse, matrix, need, pow2, product_counts, signed_convert,
    sparse_allocation, squared_error,
)


def rejected(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("accepted negative control: " + label)


def exact_exponents():
    beta, xi = Q(39, 40), Q(15, 16)
    epsilon = 1 - Q(1, 10 ** 30)
    alpha, eta = Q(99827101, 100000000), Q(332353, 332929)
    dense = epsilon - (1 - alpha) * beta
    route = epsilon - (1 - eta) * beta
    sparse = epsilon + (Q(45, 16) - 1) / 2 - xi
    scalar = epsilon - beta + Q(3, 5)
    transport = epsilon + Q(1, 2) - xi
    scans = epsilon - beta
    need(7 ** 16 < 2 ** 45 and 3 ** 5 < 2 ** 8,
         "integer-only Strassen and dense Karatsuba comparisons")
    need(sparse == epsilon - Q(1, 32), "complete sparse arithmetic exponent")
    need(0 < scans < transport < scalar < sparse < route < dense < 1,
         "all complete paid powers subordinate to dense maximum")
    need(beta + 2 * xi - 2 == Q(17, 20) < 1 and beta < Q(997, 1000),
         "actual raw-prefix precision and support-route premises")
    need(1 - epsilon < beta < epsilon, "complete context setup and balanced groups")
    need(7 ** 4 > 2 ** 11 and 3 ** 2 > 2 ** 3,
         "wrong-engine exact lower comparisons")
    wrong = epsilon + (Q(11, 4) - 1) / 2 - xi + Q(1, 2)
    need(wrong > 1, "Karatsuba substituted into sparse block bill loses the bound")
    return {"beta": str(beta), "xi": str(xi), "epsilon": str(epsilon),
            "dense": str(dense), "route": str(route), "sparse_upper": str(sparse),
            "dense_scalar_upper": str(scalar), "transport": str(transport),
            "scans_and_converters": str(scans), "wrong_sparse_scalar_lower": str(wrong),
            "native_rates_are_historical": True, "new_kappa": False}


def allocations():
    rows = []
    for n in (1, 3, 8, 31, 128):
        for g in sorted(set((1, min(3, n), min(7, n)))):
            for h in (1, 2, 16):
                for incoming in (0, 17, 509):
                    row = budget(n, g, h, 9, incoming, 5)
                    paid = sparse_allocation(row, pbar=13, sparsity=9, gamma=Q(17, 3),
                                             dense_minimum=37, descriptor=(1 << n) + 1)
                    need(paid["P"] >= incoming and paid["width"] > paid["P"],
                         "all source precision and signed-width guards")
                    for x in (-9, -1, 0, 1, 9):
                        y = signed_convert(x, incoming, paid["P"], incoming + 7, paid["width"])
                        need(Q(y, 1 << paid["P"]) == Q(x, 1 << incoming),
                             "incoming precision retained through exact conversion")
                    rows.append((n, g, h, incoming, row["stage_target"], row["local_target"],
                                 row["R2"].bit_length(), row["Rstar"].bit_length(),
                                 paid["P"], paid["width"]))
    delta = pow2(-20)
    need(64 * delta * delta > delta * delta, "whole-field norm conversion is necessary")
    local_context_error2 = 4 * (delta / 2) ** 2
    need(local_context_error2 == delta * delta and 16 * local_context_error2 > delta * delta,
         "resetting the error budget at each context is unsound")
    controls = [
        rejected(lambda: budget(0, 1, 2, 8, 0, 0), "empty complete field"),
        rejected(lambda: budget(8, 9, 2, 8, 0, 0), "axis count exceeds field bits"),
        rejected(lambda: budget(8, 2, 3, 8, 0, 0), "non-dyadic norm certificate"),
        rejected(lambda: signed_convert(1, 9, 8, 12, 12), "unpaid downward grid"),
        rejected(lambda: signed_convert(-5, 3, 3, 5, 3), "nonredundant negative width loss"),
        rejected(lambda: signed_convert(4, 3, 3, 5, 3), "nonredundant positive width loss"),
    ]
    return dict(cases=len(rows), allocation_sha256=sha256(canonical_json(rows).encode()).hexdigest(),
                negative_controls=controls, omitted_volume_fails=True,
                per_context_budget_reset_fails=True)


def ceilings():
    cases, digest = 0, sha256()
    for a in range(1, 66):
        for v in sorted(set((0, min(1, a - 1), a - 1))):
            bi = dyadic_at_least(max(2, v))
            ba = dyadic_at_least(max(2, 2 * v + 1))
            need(bi <= 4 * a and ba <= 4 * a, "least actual-band block funds row ceilings")
            for b in sorted(set((bi, ba))):
                for j in sorted(set((1, a // 2 or 1, a))):
                    for m in sorted(set((1, b // 2, b - 1, b, b + 1, 2 * b + 1))):
                        row = product_counts(a, j, m, b)
                        expanded = 8 * (Q(a, b) + 1) * (Q(2 * m, b) + 1)
                        need(row["inverse_calls"] <= expanded and row["action_calls"] <= expanded,
                             "complete expanded inverse/lifted-forward ceiling")
                        need(m * b <= 4 * a * m, "row padding absorbed without dense-boundary premise")
                        digest.update(canonical_json((a, j, m, b, row)).encode())
                        cases += 1
    small = product_counts(1, 1, 1, 8)
    need(small["inverse_calls"] == 4 and small["action_calls"] == 2
         and small["inverse_scalar_leaves"] == 4 * 343,
         "oversized block retains tiny-substream charge")
    need((2 // 8) == 0 and small["batches"] == 1, "RHS floor omits a legal entire call")
    return dict(cases=cases, exact_count_sha256=digest.hexdigest(), tiny_oversized_block=small,
                missing_rhs_ceiling_fails=True, lift_dilation_kept=True,
                real_imaginary_columns_kept=True)


def factor_and_drift_controls():
    source = matrix(((2, Q(1, 4), 0),
                     (Q(1, 3), Q(5, 3), Q(-1, 5)),
                     (0, Q(1, 7), Q(3, 2))))
    checked = []
    for ids in ((), (1,), (0, 1)):
        for broad in (False, True):
            f = five_factors(source, ids, broad=broad)
            need(f["target"] == (source if broad else inverse(source)),
                 "direct original source target independent of factor pages")
            checked.append((ids, broad, f["h"]))
    f = five_factors(source, (1,))
    x = ((Q(1, 4), Q(-1, 8)), (Q(3, 8), Q(1, 16)), (Q(-1, 4), Q(1, 8)))
    dense_exact = apply_matrix(f["factors"][0], x)
    drifted = list(dense_exact)
    drifted[0] = (drifted[0][0] + pow2(-13), drifted[0][1])
    correct = apply_matrix(f["factors"][1], drifted)
    reset_boundary = apply_matrix(f["factors"][1], dense_exact)
    need(correct != reset_boundary, "actual first dense boundary drift must enter Tlower")
    drift_error = squared_error(correct, reset_boundary)
    need(drift_error > 0, "nonzero propagated boundary drift witness")
    bad = [list(row) for row in identity(3)]
    fj = inverse(f["F"])
    for i0, i in enumerate(f["J"]):
        for j0, j in enumerate(f["J"]):
            bad[i][j] = fj[i0][j0]
    omitted_shear = apply_matrix(matrix(bad), dense_exact)
    need(omitted_shear != reset_boundary, "Schur-only substitution omits original shear")
    u, v = Q(1023, 1024), Q(1025, 1024)
    need(abs(int(v) - int(u)) > 2 * abs(v - u),
         "rounded map cannot be assigned exact map's Lipschitz constant")
    return dict(algebraic_factor_cases=len(checked), actual_reference_execution=False,
                boundary_drift_error_numerator_bits=drift_error.numerator.bit_length(),
                boundary_drift_error_denominator_bits=drift_error.denominator.bit_length(),
                boundary_reset_rejected=True, schur_only_replacement_rejected=True,
                rounded_lipschitz_shortcut_rejected=True)


def main():
    result = dict(status="PASS_EXACT_COMPLETE_JOIN_BUDGET", physical_execution=False,
                  exponents=exact_exponents(), allocations=allocations(),
                  ceilings=ceilings(), adverse_numerics=factor_and_drift_controls(),
                  scope="Exact interface inequalities and adverse algebraic controls; "
                        "actual source/physical joined replay has a separate receipt")
    print(canonical_json(result))


if __name__ == "__main__":
    main()
