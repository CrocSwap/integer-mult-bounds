#!/usr/bin/env python3
"""Small research diagnostics; no physical, compiler or theorem admission.

Decimal moments are numerical search aids, not directed interval certificates.
Row-space ranks are exact in the declared scalar model, not native oracle costs.
New code: OpenAI Codex for the repository user, Apache-2.0.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, width, field="Q"):
    require(field in ("Q", "F2"), "Only Q and F2 are implemented")
    require(all(len(row) == width for row in rows), "Inconsistent row widths")
    a = [[Fraction(x) for x in row] for row in rows]
    if field == "F2":
        require(all(x.denominator % 2 for row in a for x in row),
                "An even denominator cannot be reduced modulo two")
        a = [[x.numerator % 2 for x in row] for row in a]
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(a)) if a[i][column]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        if field == "Q":
            v = a[pivot][column]
            a[pivot] = [x / v for x in a[pivot]]
        for i in range(pivot + 1, len(a)):
            v = a[i][column]
            if field == "Q":
                a[i] = [x - v * y for x, y in zip(a[i], a[pivot])]
            else:
                a[i] = [(x - v * y) % 2 for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def cut_probe(data):
    width, field = data["width"], data.get("field", "Q")
    require(type(width) is int and width > 0, "width must be a positive integer")
    available, demanded = data["available"], data["demanded"]
    old = rank(available, width, field)
    new = rank(available + demanded, width, field)
    basis, selected = available[:], []
    current = old
    for i, row in enumerate(demanded):
        after = rank(basis + [row], width, field)
        if after > current:
            basis.append(row)
            selected.append(i)
            current = after
    return {
        "field": field, "independent_latent_coordinates": width,
        "available_rank": old, "joint_rank": new,
        "additional_answer_dimension_lower_bound": new - old,
        "residual_demand_basis_indices": selected,
        "scope": "Exact scalar linear information deficit only. All listed available rows must already be legally accessible in the same frame/version. Does not price observation production, copying, maps, volume, approximation or restoration; does not prove a native implementation attaining the bound.",
    }


def cut_controls():
    e = [[int(i == j) for j in range(6)] for i in range(6)]
    sums = [[x + y for x, y in zip(e[0], e[1])],
            [x + y for x, y in zip(e[2], e[3])]]
    correlated = cut_probe({"width": 6, "available": sums, "demanded": e[:4]})
    require(correlated["additional_answer_dimension_lower_bound"] == 2,
            "Correlated-side-information positive control failed")
    none = cut_probe({"width": 6, "available": [], "demanded": e[:4]})
    require(none["additional_answer_dimension_lower_bound"] == 4,
            "No-side-information control failed")
    drift = [[x + y for x, y in zip(e[0], e[4])], e[1],
             [x + y for x, y in zip(e[2], e[5])], e[3]]
    versioned = cut_probe({"width": 6, "available": e[:4], "demanded": drift})
    require(versioned["additional_answer_dimension_lower_bound"] == 2,
            "Changed-version control failed")
    require(rank([[1, 1], [1, -1]], 2, "Q") == 2, "Q field control failed")
    require(rank([[1, 1], [1, -1]], 2, "F2") == 1, "F2 field control failed")
    try:
        rank([["1/2"]], 1, "F2")
    except ValueError:
        pass
    else:
        raise ValueError("Even-denominator control failed")
    require(rank([], 2) == 0 and rank([[0, 0]], 2) == 0, "Zero control failed")
    return {"correlated_available_responses": correlated,
            "without_available_responses": none,
            "source_version_drift": versioned,
            "field_control_Q_rank": 2, "field_control_F2_rank": 1,
            "all_controls_passed": True,
            "warning": "Synthetic examples only; no selected-caller rows are claimed."}


def moments(profile):
    paid = {int(r): int(n) for r, n in profile["paid"].items()}
    targets = {int(r): int(n) for r, n in profile["targets"].items()}
    require(all(r > 0 and n > 0 for d in (paid, targets) for r, n in d.items()),
            "Histograms require positive ranks and counts")
    with localcontext() as ctx:
        ctx.prec = 65
        logs = {r: Decimal(r).ln() for r in set(paid) | set(targets) | {1, 8, 9, 16, 25, 145}}

        def price(r, c):
            if c == 0:
                return Decimal(r)
            return ((1 - c) * logs[r]).exp()

        def evaluate(p, t, c):
            return sum(Decimal(n) * price(r, c) for r, n in t.items()) - sum(
                Decimal(n) * price(r, c) for r, n in p.items())

        def margin(c):
            return evaluate(paid, targets, c)

        def derivative(c):
            return sum(Decimal(n) * price(r, c) * logs[r] for r, n in paid.items()) - sum(
                Decimal(n) * price(r, c) * logs[r] for r, n in targets.items())

        mass = sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items())
        require(margin(Decimal(0)) == mass, "Rank-mass control failed")
        # A source-bound control for the selected neutral completion. For a
        # different exploratory profile, this baseline-specific control is off.
        selected_profile = profile.get("base_commit") == "1a3ced60b2f7a46bc70280a04f2eeb8ca027c700"
        neutral_control = None
        if selected_profile:
            require(paid.get(8, 0) >= 144 and targets.get(8, 0) >= 144,
                    "Expected selected neutral H8 cancellation missing")
            reduced_paid, reduced_targets = paid.copy(), targets.copy()
            reduced_paid[8] -= 144
            reduced_targets[8] -= 144
            neutral_control = True
        points = []
        for s in [profile["selected_kappa"], "0.0033", "0.0034", "0.004", "0.006", "0.01"]:
            c = Decimal(s)
            m = margin(c)
            slopes = derivative(c)
            # Necessary raw-moment change only: compiler reserve/outer costs
            # would require additional slack. This is not an admission budget.
            need = max(-m, Decimal(0))
            points.append({
                "C": s, "raw_target_minus_paid": str(m),
                "raw_deficit_to_zero_before_reserves": str(need),
                "d_margin_d_C": str(slopes),
                "isolated_H1_deletions_to_cross_zero": int(need) + 1 if m <= 0 else 0,
                "alternative_extra_targets_equivalent_to_raw_deficit": {
                    str(r): str(need / price(r, c)) for r in (8, 9, 16, 25, 145)},
                "local_dC_per_removed_H1_at_this_point": str(-1 / slopes),
            })
            if selected_profile:
                reduced = evaluate(reduced_paid, reduced_targets, c)
                require(abs(m - reduced) < Decimal("1e-55"),
                        "Removing the neutral H8 pairs changed the raw margin")
                missing_target = evaluate(paid, reduced_targets, c)
                require(missing_target < m - 1000,
                        "Removing the productive H8 credit was not charged")
        lo, hi = Decimal(0), Decimal("0.02")
        require(margin(lo) > 0 and margin(hi) < 0, "No bracket in diagnostic range")
        for _ in range(100):
            mid = (lo + hi) / 2
            if margin(mid) > 0:
                lo = mid
            else:
                hi = mid
        return {"decimal_precision": ctx.prec,
                "scope": "Heuristic Decimal arithmetic; no outward error bounds, uniqueness proof, compiler reserve, physical construction or kappa admission. Equivalent target counts are isolated alternatives, not additive credits. Existing targets cannot be counted again.",
                "rank_mass_surplus_exact": mass,
                "paid_jobs_exact": sum(paid.values()),
                "productive_fields_exact": sum(targets.values()),
                "numerical_raw_sign_change_bracket": [str(lo), str(hi)],
                "neutral_144_H8_paid_target_cancellation": neutral_control,
                "points": points}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=Path(__file__).with_name("PROFILE.json"))
    parser.add_argument("--cut", type=Path, help="JSON: width, field Q/F2, available rows, demanded rows")
    parser.add_argument("--check-source-root", type=Path,
                        help="Optionally check all three frozen source hashes in an existing checkout")
    args = parser.parse_args()
    raw = args.profile.read_bytes()
    profile = json.loads(raw)
    if args.check_source_root:
        for source in profile["sources"]:
            observed = hashlib.sha256((args.check_source_root / source["path"]).read_bytes()).hexdigest()
            require(observed == source["sha256"], "Source bytes changed: " + source["path"])
        selected = json.loads((args.check_source_root / "certificates/selected-result.json").read_text())
        invoice = json.loads((args.check_source_root / "research/coupled-helper-neutral-completion/reports/expected/invoice.json").read_text())
        require(profile["paid"] == invoice["histograms"]["paid"],
                "Frozen paid histogram disagrees with its authenticated source")
        require(profile["targets"] == invoice["histograms"]["productive"],
                "Frozen target histogram disagrees with its authenticated source")
        require(profile["selected_kappa"] == selected["decimal"],
                "Frozen kappa disagrees with its authenticated source")
    result = {"status": "PASS_EXPLORATORY_DIAGNOSTICS_NO_NEW_KAPPA",
              "python": platform.python_version(),
              "base_commit": profile["base_commit"],
              "profile_sha256": hashlib.sha256(raw).hexdigest(),
              "moments": moments(profile), "synthetic_cut_controls": cut_controls()}
    if args.cut:
        result["user_cut"] = cut_probe(json.loads(args.cut.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
