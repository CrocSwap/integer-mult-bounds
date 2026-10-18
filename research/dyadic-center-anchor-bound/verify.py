#!/usr/bin/env python3
"""Offline exact replay of the constant-row shear classification and cost bound.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("center_anchor_math", HERE / "anchor.py")
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)
require = math.require
SEED = 33
SOURCE_PATHS = (
    "scripts/certify.py", "scripts/exclusion_circuit.py", "scripts/binary_phase_frames.py",
    "scripts/experiments/disjoint_tensor.py", "scripts/experiments/complex_centers.py",
    "certificates/dyadic-central-factor.json", "notes/dyadic-central-factor.tex",
    "docs/research/dyadic-central-factor.md",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def verify_sources():
    pins = load_json(HERE / "SOURCES.json")
    require(pins["base_commit"] == "47481c89fd30a43f8f882eb4b391e89c29273fd0",
            "wrong base commit")
    require(set(pins["sha256"]) == set(SOURCE_PATHS), "source coverage mismatch")
    for path in SOURCE_PATHS:
        require(sha256((ROOT / path).read_bytes()).hexdigest() == pins["sha256"][path],
                "source hash mismatch: " + path)
    return pins


def reject(call, reason):
    try:
        call()
    except ValueError as exc:
        require(reason in str(exc), "control failed for wrong reason: " + str(exc))
    else:
        raise ValueError("negative control accepted: " + reason)


def validate_factor(f, row):
    require(math.affine_identity(f) == len(f["triples"]), "incomplete affine coverage")
    v, u = math.histograms(f)
    actual_pivot = Counter(r[f["pivot"]] for r in f["scatter"])
    require({str(w): m for w, m in sorted(actual_pivot.items())} == row["pivot_numerators"],
            "pivot numerator histogram mismatch")
    require(v[-1]+v[1] == row["G"], "gather price mismatch")
    require((set(u) <= {-2, -1, 0, 1, 2}) == row["admissible"], "admissibility mismatch")
    if row["admissible"]:
        require(math.literal_price(f) == {"G": row["G"], "H": row["H"]},
                "literal cost mismatch")
    else:
        reject(lambda: math.literal_price(f), "scatter alphabet exceeded")


def small_census(h):
    pivot = SEED % h
    coordinates = [i for i in range(h) if i != pivot]
    rows = [math.orbit(h, k) for k in range(h)]
    seen = Counter()
    costs = Counter()
    admissible = original = affine_rows = 0
    for bits in range(1 << (h-1)):
        b = [i for j, i in enumerate(coordinates) if bits & (1 << j)]
        f = math.factor(h, pivot, b)
        row = rows[len(b)]
        validate_factor(f, row)
        affine_rows += len(f["triples"])
        seen[len(b)] += 1
        admissible += int(row["admissible"])
        original += int(row["original_alphabet"])
        if row["admissible"]:
            costs[row["G_plus_H"]] += 1
    require(all(seen[k] == math.choose(h-1, k) for k in range(h)),
            "incomplete anchor coverage")
    return {"h": h, "pivot": pivot, "anchors_checked": sum(seen.values()),
            "admissible_anchors": admissible, "original_alphabet_anchors": original,
            "affine_rows_checked": affine_rows, "minimum_G_plus_H": min(costs),
            "minimizers": costs[min(costs)],
            "cost_histogram": {str(c): n for c, n in sorted(costs.items())}}


def invoice(g, h, historical):
    s = historical["scalar_charge"]
    n = historical["counts"]["v"]
    invocation = 4*s["M"]+2*s["C"]+4*s["J"]+2*g+2*h
    return {"G": g, "H": h, "G_plus_H": g+h,
            "central_signed_invocation": 2*(g+h),
            "complete_signed_invocation": invocation,
            "complete_three_stage_bound": 3*n*n*invocation}


def run():
    pins = verify_sources()
    certificate = load_json(HERE / "CERTIFICATE.json")
    math.check_positive_certificate(certificate["positive_newton_coefficients"])

    # Exact binding to the inherited executable factor, not just its prose.
    sys.path.insert(0, str(ROOT / "scripts"))
    from experiments.complex_centers import factor as reference_factor
    reference_rows = 0
    for h in (8, 10, 26):
        reference = reference_factor(h)
        ours = math.factor(h, 0, (1, 2))
        dense_gather = [tuple(dict(v).get(i, 0) for i in range(h))
                        for v in reference["gather"]]
        require(reference["triples"] == ours["triples"] and
                reference["scatter"] == ours["scatter"] and dense_gather == ours["gather"],
                "historical factor mismatch")
        reference_rows += len(ours["triples"])

    small = [small_census(h) for h in (8, 10)]
    pivot = SEED % 26
    coordinates = [i for i in range(26) if i != pivot]
    orbits = []
    affine_rows = 0
    for k in range(26):
        row = math.orbit(26, k)
        f = math.factor(26, pivot, coordinates[:k])
        validate_factor(f, row)
        affine_rows += len(f["triples"])
        require(row["admissible"] == (k <= 4), "signed alphabet classification failed")
        require(row["original_alphabet"] == (k <= 3), "original alphabet classification failed")
        orbits.append(row)
    require(sum(r["anchors"] for r in orbits) == 2**25, "incomplete h26 orbit coverage")
    allowed = [r for r in orbits if r["admissible"]]
    minimum = min(r["G_plus_H"] for r in allowed)
    require([r["k"] for r in allowed if r["G_plus_H"] == minimum] == [0],
            "h26 minimizer mismatch")

    # Literal four-step commutator, all independent inputs, both signs.
    replay_columns = 0
    for h in (8, 10):
        p = SEED % h
        coordinates = [i for i in range(h) if i != p]
        for k in range(5):
            for inverse in (False, True):
                counted = math.orbit(h, k)
                replay = math.central_replay(math.factor(h, p, coordinates[:k]), inverse,
                                            billed=2*counted["G_plus_H"])
                replay_columns += replay["input_columns"]

    historical = load_json(ROOT / "certificates/dyadic-central-factor.json")
    old = math.literal_price(math.factor(26, 0, (1, 2)))
    require(old["G"] == historical["central_factor"]["gather_steps"] and
            old["H"] == historical["central_factor"]["scatter_steps"],
            "historical invoice mismatch")
    old_bill = invoice(old["G"], old["H"], historical)
    require(old_bill["complete_three_stage_bound"] == historical["scalar_charge"]["steps"],
            "complete historical scalar charge mismatch")
    invoices = [dict(k=r["k"], **invoice(r["G"], r["H"], historical)) for r in allowed]

    controls = []
    for bad in (-1, 2):
        offsets = [0]*26
        offsets[0] = bad
        reject(lambda: math.classify_integral_anchor(26, pivot, offsets), "gather alphabet exceeded")
        controls.append("integral anchor " + str(bad))
    offsets = [0]*26
    offsets[0] = True
    reject(lambda: math.classify_integral_anchor(26, pivot, offsets), "integral anchor required")
    controls.append("boolean anchor")
    reject(lambda: math.literal_price(math.factor(26, pivot, [0, 1, 2, 3, 4])),
           "scatter alphabet exceeded")
    controls.append("five-anchor numerator -3")
    reject(lambda: math.literal_price(math.factor(8, 1, [0, 2, 3, 4]), original_alphabet=True),
           "scatter alphabet exceeded")
    controls.append("minus two excluded by original guard")
    f = math.factor(8, 1, [])
    bad = deepcopy(f)
    bad["scatter"][0] = tuple(0 for _ in range(8))
    reject(lambda: math.affine_identity(bad), "central affine identity failed")
    controls.append("missing conjugate scatter")
    bad = deepcopy(f)
    bad["gather"][0] = tuple(0 for _ in range(8))
    reject(lambda: math.affine_identity(bad), "gather form mismatch")
    controls.append("missing constant gather")
    for name, message in (("restore", "dirty centers not restored"),
                          ("compensate", "dirty target shear failed"),
                          ("deliver", "dirty target shear failed")):
        reject(lambda: math.central_replay(f, omit=name), message)
        controls.append("missing " + name)
    bad = deepcopy(certificate["positive_newton_coefficients"])
    bad[1][0] += 1
    reject(lambda: math.check_positive_certificate(bad), "polynomial identity failed")
    controls.append("incorrect polynomial coefficient")
    bad[0][0] = -1
    reject(lambda: math.check_positive_certificate(bad), "nonpositive certificate")
    controls.append("negative positivity witness")
    # The threshold and cleanup controls are comparisons against exact prices.
    require(small[0]["minimum_G_plus_H"] == 702 < math.orbit(8, 0)["G_plus_H"],
            "h8 counterexample lost")
    controls.append("h8 refutes extending h>=10 optimum to h8")
    reject(lambda: math.central_replay(f, billed=math.orbit(8, 0)["G_plus_H"]),
           "executed central bill mismatch")
    controls.append("one gather/scatter pair undercharged")

    return {"status": "SCOPED NEGATIVE RESULT; NO NEW KAPPA", "assignment_seed": SEED,
            "base_commit": pins["base_commit"], "h26_pivot": pivot,
            "h26_binary_anchors": 2**25,
            "h26_admissible_anchors": sum(r["anchors"] for r in allowed),
            "h26_original_alphabet_anchors": sum(r["anchors"] for r in orbits if r["original_alphabet"]),
            "h26_minimum_G_plus_H": minimum, "h26_unique_minimizer_k": 0,
            "h26_orbits": orbits, "h26_affine_rows_checked": affine_rows,
            "small_complete_censuses": small, "historical_reference_rows": reference_rows,
            "central_basis_column_direction_obligations": replay_columns,
            "positive_newton_coefficients": certificate["positive_newton_coefficients"],
            "historical_invoice": old_bill, "h26_complete_invoices": invoices,
            "negative_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only this package's EXPECTED.json")
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / "EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(canonical(result) == canonical(load_json(HERE / "EXPECTED.json")),
                "expected receipt mismatch")
    print("PASS_CENTER_ANCHOR_BOUND h=26 orbits=26 admissible=15276 optimum=42600 "
          "all_even_h_ge_10 controls=14 no_new_kappa")


if __name__ == "__main__":
    main()
