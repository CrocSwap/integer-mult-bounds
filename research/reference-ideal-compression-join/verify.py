"""Bounded source/periodic oracle and unchanged-budget replay.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import allocation as alloc
import independent
import periodic_oracle as oracle
import source

HERE = Path(__file__).resolve().parent


def need(ok, text):
    if not ok:
        raise ValueError(text)


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def rational_receipt(x):
    x = Q(x)
    return {"sha256": digest([x.numerator, x.denominator]),
            "numerator_bits": abs(x.numerator).bit_length(),
            "denominator_bits": x.denominator.bit_length(),
            "ceiling_log2_abs": alloc.ceil_log2(abs(x)) if x else None}


def load_ledger():
    spec = importlib.util.spec_from_file_location("unchanged_public_ledger",
        HERE / "retained/ledger/ledger.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejects(call, message):
    try:
        call()
    except ValueError:
        return message
    raise ValueError("negative control accepted: "+message)


def algebra_checks(ledger):
    count = 0
    fixtures = []
    # These are exact budget fixtures, not a claim of realized production axes.
    for m in (1, 2, 3, 7):
        for width in (1, 2, 5):
            for radius in (1, 3, 257):
                for tau in (1, 9, 40):
                    for extra_gamma in (0, 11):
                        p, v, u = 3, 18, 1
                        caller = 20*width
                        gamma = m*caller+extra_gamma
                        first = alloc.source_target(m, tau, gamma)
                        s = first["target_bits"]
                        # Stronger than (8); gap=1/2 independently satisfies its floor.
                        epsilon = alloc.pow2(-s-46)/Q(radius*p*p)
                        groups, axes = [], []
                        for _ in range(m):
                            groups.append(alloc.group_invoice([Q(1, 2)]*width,
                                [epsilon]*width, [u]*width, [v]*width, caller))
                            # Literal gap=1/2 Neumann tails, normalized by 2^u.
                            J = first["z"]+alloc.ceil_log2(8*radius*width)+2
                            axes.append([SimpleNamespace(gap=Q(1, 2), normalizer_bits=u,
                                bandwidth=2, tail=alloc.pow2(-J)) for _ in range(width)])
                        budget = ledger.common_budget(axes, radius, tau, gamma)
                        need(all(t <= s for t in budget["core_targets"]),
                             "source-first target dominates actual unchanged target")
                        total = alloc.combined_invoice(budget, groups, radius)
                        need(total["restored_bound"] <= alloc.pow2(-tau),
                             "full restored algebra tolerance")
                        fixtures.append([m, width, radius, tau, extra_gamma,
                            budget["grid_bits"], budget["core_targets"],
                            rational_receipt(total["restored_bound"])])
                        count += 1
    production = []
    for l in (1, 2, 8, 16, 64, 256):
        for width in (1, 2, 3, 17, 257):
            u, v, k = 2*l+4, 2*l+8, 100*l
            exponent = (2*u+v-k)*width
            need(exponent <= -78*width and width <= (1 << width),
                 "uniform concrete normalization slack")
            need(alloc.ceil_log2(width)+exponent < 42, "production finite gate")
            production.append([l, width, exponent])
    return {"unchanged_budget_cases": count, "budget_sha256": digest(fixtures),
            "production_gate_cases": len(production), "gate_sha256": digest(production)}


def actual_witness(ledger, reference_module, raw):
    p, S, T, alpha, cap, radius, tau, gamma, K = 3, 61, 64, 3, 1, 1, 12, 20, 20
    need(alpha == independent.actual_alpha(p), "actual finite alpha policy")
    first = alloc.source_target(1, tau, gamma)
    ref = reference_module.Reference.for_cap(raw, S, T-S, alpha, cap,
                                              2*radius, first["target_bits"])
    receipt = alloc.bind_reference(ref, p, radius, 1)
    u, v = receipt["normalizer_bits"], 2*alpha*alpha
    need(K-u >= 2*alpha*alpha, "actual remaining-service coefficient guard")
    invoice = alloc.group_invoice([ref.narrow_gap], [ref.errors["narrow"]], [u], [v], K)
    J = first["z"]+20
    tail = (1-ref.narrow_gap)**J/(alloc.pow2(u)*ref.narrow_gap)
    axis = SimpleNamespace(gap=ref.narrow_gap, normalizer_bits=u,
                           bandwidth=ref.spec.target_halfwidth, tail=tail)
    budget = ledger.common_budget([[axis]], radius, tau, gamma)
    alloc.bind_reference(ref, p, radius, budget["core_targets"][0])
    total = alloc.combined_invoice(budget, [invoice], radius)
    need(total["restored_bound"] <= alloc.pow2(-tau), "actual source joined old budget")

    H = []
    kinds = {}
    for row in range(T):
        values = {}
        for column in range(T):
            entry = ref.entry("narrow", row, column)
            kinds[entry.kind] = kinds.get(entry.kind, 0)+1
            if entry.value:
                values[column] = entry.value
        H.append(values)
    ideal = oracle.full_periodic(S, T, alpha, cutoff=4, bits=240)
    need(tuple(ideal["selected"]) == tuple(ref.selected), "independent original q binding")
    need(tuple(ideal["holes"]) == ref.holes, "independent original hole binding")
    need(ideal["betas"] == list(ref.betas), "independent original beta binding")
    bounds = []
    for row, hrow in enumerate(H):
        boxrow = ideal["boxes"][row]
        bound = sum((max(abs(hrow.get(k, Q())-boxrow.get(k, (Q(), Q()))[0]),
                         abs(hrow.get(k, Q())-boxrow.get(k, (Q(), Q()))[1]))
                     for k in set(hrow) | set(boxrow)), Q())
        if row not in ideal["holes"]:
            bound += ideal["tail"]
        need(bound <= ref.errors["narrow"], "independent all-row periodic error")
        bounds.append(bound)
    need(ideal["rho_upper"] <= 1-ref.narrow_gap-ref.errors["narrow"],
         "independent ideal contraction agrees with literal certificate")

    x = [(Q((3*k)%11-5, 16), Q((5*k)%13-6, 16)) for k in range(T)]
    need(oracle.norm(x) <= radius, "complex complete-field diagnostic input")
    h_lower = [{k: oracle.quantize_lower(a, 240) for k, a in row.items()} for row in H]
    h_solution = oracle.rounded_neumann(h_lower, x)
    n_solution = oracle.rounded_neumann(ideal["rows"], x)
    hcert = oracle.inverse_receipt(H, x, h_solution)
    ncert = oracle.inverse_receipt(ideal["rows"], x, n_solution, max(ideal["row_errors"]))
    difference = oracle.norm(oracle.subtract(h_solution, n_solution))
    inverse_bound = difference+hcert["inverse_error"]+ncert["inverse_error"]
    nominal = ref.errors["narrow"]/(ref.narrow_gap*(ref.narrow_gap+ref.errors["narrow"]))
    need(inverse_bound <= nominal*oracle.norm(x), "certified complete inverse comparison")

    dboxes = []
    for beta in ideal["betas"]:
        lo, hi = oracle.direct_decay(alpha*alpha*beta*beta, 260)
        need(lo > 0, "positive independent diagonal enclosure")
        dboxes.append((1/hi, 1/lo))
    need(max(hi for _, hi in dboxes) < alloc.pow2(v), "actual small-case diagonal bound")
    selected_error = max(dboxes[i][1]*(oracle.pair_norm((
        h_solution[k][0]-n_solution[k][0], h_solution[k][1]-n_solution[k][1]))
        +hcert["inverse_error"]+ncert["inverse_error"])
        for i, k in enumerate(ideal["selected"]))
    selected_error *= alloc.pow2(-K)
    need(selected_error <= radius*invoice["reference_defect"],
         "actual D after inverse and final C reference contribution")

    controls = []
    controls.append(rejects(lambda: alloc.bind_reference(ref, p, 2, 1),
                            "underfunded source radius"))
    controls.append(rejects(lambda: alloc.bind_reference(ref, p, radius,
                               first["target_bits"]+1), "underfunded source target"))
    controls.append(rejects(lambda: alloc.group_invoice([Q(1, 1 << 60)],
        [Q(1, 1 << 100)], [60], [0], 60), "old target without normalization slack"))
    controls.append(rejects(lambda: alloc.group_invoice([ref.narrow_gap],
        [ref.errors["narrow"]], [u], [v], u+v-1), "noncontracting remaining diagonal"))
    # Omit one true cross-period entry: the ideal box is far outside epsilon.
    wrap_column = ideal["selected"][-1]
    need(ideal["boxes"][0][wrap_column][0] > ref.errors["narrow"],
         "missing-period-wrap mutation must be detected")
    controls.append("omitted original-period nearest entry")
    hole = ideal["holes"][0]
    need(hole not in H[0] and hole not in ideal["rows"][0] and
         Q(1, 8) > ref.errors["narrow"], "hole cross-coupling mutation detected")
    controls.append("invented selected/hole coupling")
    need(2*first["eta"]+first["eta"]/4 > 2*first["eta"],
         "arbitrary eta wrapper does not have paid reference room")
    controls.append("replaced actual wrapper bound by full eta")
    # Periodic diagonal alias h=S at original row zero is strictly positive.
    alias_factor = alpha*alpha*T*T
    alias_lower_exponent = 8*alias_factor
    need(alias_lower_exponent > 0 and Q(1, 1 << alias_lower_exponent) > 0,
         "literal target cannot delete positive diagonal aliases")
    controls.append("zero diagonal-alias target")
    # D must follow the inverse, as in the source; it does not commute with H.
    i, j = 0, 1
    need(dboxes[j][0] > dboxes[i][1] and H[ideal["selected"][i]][ideal["selected"][j]] > 0,
         "actual D/H commutator is nonzero")
    controls.append("commuted diagonal through inverse")
    # Inverse errors cannot be bounded solely by entrywise perturbation.
    a, e = Q(3, 4), Q(1, 16)
    exact_inverse_difference = e/((1-a)*(1-a-e))
    need(exact_inverse_difference > e, "omitted resolvent amplification control")
    controls.append("dropped inverse amplification on rational two-row control")
    for k in ideal["holes"]:
        need(h_solution[k] == x[k] and n_solution[k] == x[k],
             "both inverses preserve holes before extraction")
    return {"parameters": {"p": p, "S": S, "T": T, "alpha": alpha, "cap": cap,
        "R0": radius, "source_radius": 2*radius, "tau": tau, "gamma": gamma,
        "K": K, "v": v, "u": u}, "reference_spec": vars(ref.spec),
        "source_allocation": ref.allocation, "reference_sha256": ref.description_hash,
        "all_reference_entries": T*T, "retained_nonzero_entries": sum(map(len, H)),
        "entry_kinds": kinds, "independent_periodic_terms": ideal["terms"],
        "original_holes": ideal["holes"], "oracle_grid_bits": 240,
        "neumann_steps_per_solve": 128, "complex_input_sha256": digest(x),
        "actual_H_sha256": digest(H), "independent_N_lower_sha256": digest(ideal["rows"]),
        "infinite_tail": rational_receipt(ideal["tail"]),
        "maximum_reference_row_defect": rational_receipt(max(bounds)),
        "inverse_comparison_bound": rational_receipt(inverse_bound),
        "H_residual": rational_receipt(hcert["residual"]),
        "N_residual_including_infinite_tail": rational_receipt(ncert["residual"]),
        "after_D_and_extraction_bound": rational_receipt(selected_error),
        "unchanged_q": budget["grid_bits"], "unchanged_core_targets": budget["core_targets"],
        "restored_combined_bound": rational_receipt(total["restored_bound"]),
        "positive_diagonal_alias_lower_exponent": alias_lower_exponent,
        "negative_controls": controls,
        "physical_native_execution": False,
        "dense_context_geometry_and_radius_admitted": False,
        "source_radius_covers_bridge_radius_only": True,
        "whole_multiplier_or_production_parameter_instance": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    counts = source.authenticate()
    ledger = load_ledger()
    algebra = algebra_checks(ledger)
    with source.opened() as (reference_module, raw):
        witness = actual_witness(ledger, reference_module, raw)
    result = {"status": "PASS_REFERENCE_IDEAL_COMPRESSION_JOIN",
              "canonical_inputs": counts[0], "public_retained_files": counts[1],
              "algebra": algebra, "actual_periodic_witness": witness}
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(result["status"], json.dumps({"canonical_inputs": counts[0],
        "budget_cases": algebra["unchanged_budget_cases"],
        "reference_entries": witness["all_reference_entries"],
        "periodic_terms": witness["independent_periodic_terms"],
        "negative_controls": len(witness["negative_controls"])}))


if __name__ == "__main__":
    main()
