#!/usr/bin/env python3
"""Exact bounds for one nested-width realization; no native or outer admission.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
The finite-flow oracle is zxv's unchanged PR4436 implementation of the
Jacob Alan Sussman construction; it is authenticated before execution.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        need(all(not p.is_symlink() for p in (path, *path.parents) if p != ROOT.parent),
             "symlinked input: " + row["path"])
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"], "changed input: " + row["path"])
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        need(sha1(blob).hexdigest() == row["git_blob"], "changed Git blob: " + row["path"])
        result[row["path"]] = raw
    return result


def ceildiv(n, d):
    return (n + d - 1) // d


def legacy_ulog2(x):
    """The predecessor's deliberately upward bit-length bound, including at powers of two."""
    x = Q(x)
    return x.numerator.bit_length() - (x.denominator.bit_length() - 1)


def product_inventory(inv, power):
    out = Counter({1: 1})
    for _ in range(power):
        following = Counter()
        for x, nx in out.items():
            for y, ny in inv.items():
                following[x * y] += nx * ny
        out = following
    return out


def literal_completion(targets, paid, power, floor, cutoff):
    """Small exact product/pad/split oracle, not an emitted native word."""
    t = product_inventory(targets, power)
    p = product_inventory(paid, power)
    L, J = floor ** power, cutoff ** power
    completed = Counter()
    for rank, count in t.items():
        completed[max(L, rank)] += count
        if rank < L:
            p[L - rank] += count
    split = Counter()
    for rank, count in p.items():
        q, r = divmod(rank, J)
        split[J] += q * count
        if r:
            split[r] += count
    return +completed, +split


def paid_count_bound(targets, paid, power, floor, cutoff):
    W = sum(targets.values()) ** power
    original = sum(paid.values()) ** power
    mass = sum(k * n for k, n in paid.items()) ** power
    L, J = floor ** power, cutoff ** power
    return original + ceildiv(mass, J) + W * ceildiv(L, J)


def floor_multiplicity_lower(targets, power, floor):
    return sum(count for rank, count in targets.items() if rank <= floor) ** power


def height_bounds(H, M, L):
    lower = (H - M.bit_length()) // L.bit_length()
    upper = (H - (M.bit_length() - 1)) // (L.bit_length() - 1)
    return lower, upper


def rejects(check, name):
    try:
        check()
    except ValueError:
        return name
    raise ValueError("negative control accepted: " + name)


def finite_checks(Flow, selected):
    profiles = [({2: 2, 5: 1}, {1: 2}),
                ({2: 1, 5: 1}, {1: 2, 4: 1}),
                ({3: 2}, {1: 3, 2: 1}),
                ({3: 1, 9: 1}, {1: 1})]
    rows, literal_cases, nested_cases, height_cases = [], 0, 0, 0
    for targets, paid in profiles:
        m, L = max(targets), min(targets)
        W, A, C = sum(targets.values()), targets[L], sum(targets.values()) + sum(paid.values()) + 1
        B = 1
        for n in range(m, 97):
            flow = Flow(targets, paid, n)
            got = flow.merged()
            h, S = got["height"], got["source_count"]
            if n & (n - 1) == 0:
                lo, hi = height_bounds(n.bit_length() - 1, m, L)
                need(lo <= h <= hi, "height bounds against exact source flow")
                height_cases += 1
            need(W * A ** h <= S <= W * C ** (h + 1), "finite source-count envelope")
            B *= S
            need(B <= (W * C ** (h + 1)) ** n, "finite nested-width upper bound")
            if h >= 1:
                need(B >= (W * A ** (h - 1)) ** (n - n // L), "finite nested-width lower bound")
                nested_cases += 1
            if n in {m, m * L, m * L * L}:
                word = [r for r, count in paid.items() for _ in range(count)]
                literal = flow.literal(word)
                need(literal["sources"] == got["sources"] and literal["exits"] == got["exits"],
                     "literal/merged chronological flow disagreement")
                literal_cases += 1
            rows.append([sorted(targets.items()), sorted(paid.items()), n, h, S])
    products = 0
    for targets, paid, b, c in [({2: 2, 5: 1}, {1: 2, 3: 1}, 3, 2),
                                ({2: 1, 9: 1}, {1: 3}, 3, 2),
                                ({2: 10, 5: 1}, {1: 1}, 4, 2)]:
        for v in range(1, 5):
            t, p = literal_completion(targets, paid, v, b, c)
            A = floor_multiplicity_lower(targets, v, b)
            need(t[b ** v] >= A, "completed minimum-target multiplicity")
            need(sum(p.values()) <= paid_count_bound(targets, paid, v, b, c), "complete paid-count bound")
            target_mass = sum(k * count for k, count in t.items())
            paid_mass = sum(k * count for k, count in p.items())
            expected_surplus = sum(k * count for k, count in targets.items()) ** v - sum(k * count for k, count in paid.items()) ** v
            need(target_mass - paid_mass == expected_surplus, "product/completion/split rank-mass conservation")
            products += 1
    raw_t = {int(k): n for k, n in selected["targets"].items()}
    raw_p = {int(k): n for k, n in selected["paid"].items()}
    b, c = selected["strictification"]["floor"], selected["strictification"]["cutoff"]
    reduced_t, reduced_p = literal_completion(raw_t, raw_p, 1, b, c)
    m, L, W, A = max(reduced_t), min(reduced_t), sum(reduced_t.values()), reduced_t[min(reduced_t)]
    C = W + sum(reduced_p.values()) + 1
    calibration = []
    for n in (m, m * L - 1, m * L, m * L * L - 1, m * L * L, m * L * L + 1):
        got = Flow(reduced_t, reduced_p, n).merged()
        h, S = got["height"], got["source_count"]
        need(W * A ** h <= S <= W * C ** (h + 1), "selected v=1 source calibration")
        calibration.append([n, h, S])
    controls = []
    t, p = literal_completion({2: 10, 5: 1}, {1: 1}, 1, 4, 2)
    controls.append(rejects(lambda: need(sum(p.values()) <= 2, "omitted paid completion"), "omitted-completion"))
    controls.append(rejects(lambda: need(10 <= ceildiv(10, 2), "omitted per-call rounding"), "omitted-split-rounding"))
    t, _ = literal_completion({2: 1, 9: 1}, {1: 1}, 1, 3, 2)
    controls.append(rejects(lambda: need(t[3] >= 2, "unqualified productive floor credit"), "all-targets-counted-at-floor"))
    tiny = Flow({3: 1, 9: 1}, {1: 1}, 27).merged()
    controls.append(rejects(lambda: need(tiny["source_count"] >= 2 * 2 ** tiny["height"], "inflated root multiplicity"), "inflated-root-lower-bound"))
    actual_height = Flow({3: 1, 9: 1}, {1: 1}, 256).G
    wrong_upper = (8 - (9).bit_length()) // (3).bit_length()
    controls.append(rejects(lambda: need(actual_height <= wrong_upper, "wrong height rounding direction"), "height-rounding-direction"))
    return {"source_flows": len(rows), "literal_flows": literal_cases,
            "nested_width_lower_checks": nested_cases, "height_bound_checks": height_cases,
            "product_pad_split_cases": products,
            "selected_v1_source_calibration": calibration,
            "source_rows_sha256": sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest(),
            "negative_controls": controls}


def selected_envelope(j):
    targets = {int(k): n for k, n in j["targets"].items()}
    paid = {int(k): n for k, n in j["paid"].items()}
    v, b, c = (j["strictification"][k] for k in ("power", "floor", "cutoff"))
    H = j["compiler"]["H"]
    need((v, b, c, H) == (1024, 21, 20, 64215200000000), "selected PR4470 parameter context")
    W, L, M = sum(targets.values()) ** v, b ** v, max(targets) ** v
    A = floor_multiplicity_lower(targets, v, b)
    pbar = paid_count_bound(targets, paid, v, b, c)
    C = W + pbar + 1
    # M*L^h <= 2^H: upper logs give a lower height; lower logs give an upper height.
    h_lower, h_upper = height_bounds(H, M, L)
    need(h_lower >= 1, "nonempty lower slab")
    x_lower = W.bit_length() - 1 + (h_lower - 1) * (A.bit_length() - 1)
    x_upper = W.bit_length() + (h_upper + 1) * C.bit_length()
    # These compare coefficients, with N canceled; N itself is never instantiated.
    need(1000 * (L - 1) * x_lower > 2943 * L * H, "lower K/N > 2943/1000")
    need(1000 * x_upper < 3639 * H, "upper K/N < 3639/1000")
    need(4 * x_upper * L < 5 * (L - 1) * x_lower, "coefficient bracket ratio < 5/4")
    need(x_upper < 4 * H, "K < 4N for conservative outer substitution")
    return {"H": H, "N": f"2^{H}", "tensor_power": v,
            "raw_productive_count": sum(targets.values()), "raw_paid_count": sum(paid.values()),
            "raw_paid_mass": sum(k * n for k, n in paid.items()),
            "raw_targets_at_most_floor": floor_multiplicity_lower(targets, 1, b),
            "floor_base": b, "cutoff_base": c, "ambient_base": max(targets),
            "floor_log2_bounds": [L.bit_length() - 1, L.bit_length()],
            "ambient_log2_bounds": [M.bit_length() - 1, M.bit_length()],
            "height_lower": h_lower, "height_upper": h_upper,
            "W_log2_upper": W.bit_length(), "A_log2_lower": A.bit_length() - 1,
            "W_plus_paid_bound_plus_one_log2_upper": C.bit_length(),
            "x_lower": x_lower, "x_upper": x_upper,
            "K_over_N_strict_bounds": ["2943/1000", "3639/1000"],
            "bracket_ratio_strict_upper": "5/4"}


def fit(log2_C):
    """Least positive integer L for the predecessor's displayed upward threshold.

    Partition by bit length instead of presuming the stepwise predicate is monotone.
    """
    delta, beta = Q(1, 250), Q(69999991, 70000000)
    candidates = []
    for bits in range(1, 65):
        required = Q(log2_C + 10 + 3 * bits) / ((1 - delta) * beta)
        L = max(1 << (bits - 1), ceildiv(required.numerator, required.denominator))
        if L < 1 << bits:
            candidates.append(L)
    need(bool(candidates), "threshold search range exhausted")
    answer = min(candidates)
    predicate = lambda L: Q(log2_C + 10 + 3 * legacy_ulog2(L)) / (1 - delta) <= beta * L
    need(predicate(answer) and not predicate(answer - 1), "adjacent threshold signs")
    return answer


def outer_accounting(j, old):
    H = j["compiler"]["H"]
    v = j["strictification"]["power"]
    W = sum(j["targets"].values()) ** v
    MP = sum(int(k) * n for k, n in j["paid"].items()) ** v
    b = j["strictification"]["floor"]
    old_x = legacy_ulog2(W) + (H + 1) * legacy_ulog2(W + MP + W * b ** v + 1)
    width_factor = legacy_ulog2(legacy_ulog2(232960) + 3)
    previous_complex = H + legacy_ulog2(Q(old_x + 1, H)) + width_factor + 1
    need(previous_complex == 64215200000022, "PR4972 complex-share positive control")
    Hb = old["bit_strictification"]["uniform_H1"]
    bit_small = legacy_ulog2(Q(2 * (5 * Hb + 27) + 1, Hb))
    inherited_bit = 2 * Hb + bit_small + 1 + width_factor + 1
    need(inherited_bit == 51973930319885, "unchanged predecessor BIT-share arithmetic")
    # K < 4N replaces only the complex-width bound; retain c_row=1 and all other tariffs.
    new_complex = H + 2 + width_factor + 1
    previous_C = max(previous_complex, inherited_bit, 74) + 2
    new_C = max(new_complex, inherited_bit, 74) + 2
    need((previous_C, new_C) == (64215200000024, 64215200000010), "outer accounting comparison")
    return {"assumed_c_row": 1, "inherited_Cw": 232960, "inherited_log2_A_old_upper": 64,
            "unchanged_BIT_share_log2_upper": inherited_bit,
            "previous_complex_share_log2_upper": previous_complex,
            "new_complex_share_log2_upper": new_complex,
            "previous_log2_C_upper": previous_C, "new_log2_C_upper": new_C,
            "previous_fit_log2_p": fit(previous_C), "new_fit_log2_p": fit(new_C),
            "scope": "Same conservative outer-accounting formula and inherited tariffs; not optimal C or supplier admission."}


def main():
    need(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    inputs = authenticated_inputs()
    module = ModuleType("authenticated_pr4436_flow")
    name = "research/direct-mixed-flow/flow.py"
    exec(compile(inputs[name], name, "exec"), module.__dict__)
    j = json.loads(inputs["research/joint-helper-lattice/RESULT.json"])
    old = json.loads(inputs["research/query-thinned-controllers/RESULT.json"])
    result = {"schema_version": 1, "evidence_level": "author-checked",
              "selected_kappa_unchanged": "60403/20000000",
              "envelope": selected_envelope(j), "finite_checks": finite_checks(module.Flow, j),
              "conditional_outer_accounting": outer_accounting(j, old)}
    need(authenticated_inputs() == inputs, "source bytes changed during replay")
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8")), "changed result receipt")
        print("PASS_SELECTED_COMPLEX_WIDTH_ENVELOPE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_SELECTED_COMPLEX_WIDTH_ENVELOPE: " + str(exc), file=sys.stderr)
        sys.exit(1)
