#!/usr/bin/env python3
"""Exact height-1 source count for the selected nested-width rule.

unpaidmoon, with substantial Cursor Grok assistance. Apache-2.0.
The flow oracle is zxv's PR4436 implementation and is authenticated before use.
This does not replace JoyboyBrian's uniform first-moment envelope.
"""
from collections import Counter
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
    """Product, completion to the floor, then splitting at the cutoff."""
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


def ceildiv(n, d):
    return (n + d - 1) // d


def paid_count_bound(targets, paid, power, floor, cutoff):
    W = sum(targets.values()) ** power
    original = sum(paid.values()) ** power
    mass = sum(k * n for k, n in paid.items()) ** power
    L, J = floor ** power, cutoff ** power
    return original + ceildiv(mass, J) + W * ceildiv(L, J)


def height1_count(targets, paid, cap):
    """S = W*A(cap) + P*(W-A(cap)) when rmax < L <= cap < L*L."""
    L = min(targets)
    rmax = max(paid)
    need(rmax < L <= cap < L * L, "height-1 rank contract")
    need(all(rank >= L for rank in targets), "completed targets lie at or above L")
    W = sum(targets.values())
    P = sum(paid.values())
    A = sum(count for rank, count in targets.items() if rank <= cap)
    return W * A + P * (W - A), W, A, P


def rejects(check, name):
    try:
        check()
    except ValueError:
        return name
    raise ValueError("negative control accepted: " + name)


def unchecked(targets, paid, cap):
    W = sum(targets.values())
    P = sum(paid.values())
    A = sum(count for rank, count in targets.items() if rank <= cap)
    return W * A + P * (W - A)


def small_profiles(Flow):
    profiles = [({2: 2, 5: 1}, {1: 2}),
                ({3: 2}, {1: 3, 2: 1}),
                ({4: 3, 6: 1}, {1: 1}),
                ({5: 1, 8: 2, 9: 1}, {1: 2, 3: 1, 4: 1})]
    caps = 0
    literal = 0
    for targets, paid in profiles:
        L, m = min(targets), max(targets)
        W = sum(targets.values())
        for cap in range(L, L * L):
            predicted, _, A, _ = height1_count(targets, paid, cap)
            got = Flow(targets, paid, cap * m).merged()
            need(got["height"] == 1, "small profile height")
            need(got["source_count"] == predicted, "small profile height-1 count")
            if cap >= m:
                need(predicted == W * W, "full-support square")
            need(predicted - W * W == (W - A) * (sum(paid.values()) - W), "square gap identity")
            caps += 1
        word = [r for r, count in paid.items() for _ in range(count)]
        n = L * m
        flow = Flow(targets, paid, n)
        replay = flow.literal(word)
        need(sum(replay["sources"].values()) == flow.merged()["source_count"],
             "literal/merged height-1 disagreement")
        literal += 1
    return caps, literal


def selected_slab(Flow, targets, paid):
    L, m = min(targets), max(targets)
    W = sum(targets.values())
    P = sum(paid.values())
    need((L, m, max(paid), W, P) == (21, 145, 20, 10928, 77564), "v=1 completed invoice")
    need(sum(count for rank, count in targets.items() if rank <= 21) == 7792, "floor multiplicity")
    rows = []
    previous = None
    for cap in range(L, L * L):
        predicted, _, A, _ = height1_count(targets, paid, cap)
        got = Flow(targets, paid, cap * m).merged()
        need(got["height"] == 1 and got["source_count"] == predicted, "selected height-1 slab")
        if cap >= m:
            need(predicted == W * W, "square window")
        if previous is not None:
            need(predicted - previous[0] == (W - P) * (A - previous[1]), "cap step")
        previous = (predicted, A)
        if cap in (21, 25, 145, 440):
            rows.append({"cap": cap, "n": cap * m, "A": A, "S": predicted})
    start, end = rows[0]["S"], rows[-1]["S"]
    need(start == 328391680 and end == 119421184, "published height-1 endpoints")
    need(start - end == (P - W) * (W - 7792), "published drop")
    need(start > end, "height-1 source count falls")
    return {"caps": L * L - L, "samples": rows, "start_S": start, "end_S": end,
            "drop": start - end}


def negative_controls(Flow, targets, paid):
    controls = []

    def rmax_fails():
        bad_t, bad_p, cap = {3: 1, 8: 1}, {5: 1}, 4
        got = Flow(bad_t, bad_p, cap * max(bad_t)).merged()
        need(got["source_count"] == unchecked(bad_t, bad_p, cap), "rmax below the floor")

    def truncation_optional():
        need(10928 * 7792 == 328391680, "truncation term optional")

    def height_two():
        got = Flow(targets, paid, 63945).merged()
        need(got["height"] == 1 and got["source_count"] == 10928 ** 2, "formula at the next rank")

    def square_lower():
        bad_t, bad_p, cap = {4: 3, 6: 1}, {1: 1}, 4
        got = Flow(bad_t, bad_p, cap * max(bad_t)).merged()
        need(got["source_count"] >= sum(bad_t.values()) ** 2, "partial-cap square lower bound")

    controls.append(rejects(rmax_fails, "paid-rank-at-least-L"))
    controls.append(rejects(truncation_optional, "omit-truncated-term"))
    controls.append(rejects(height_two, "height-two-extension"))
    controls.append(rejects(square_lower, "square-lower-bound-when-P-below-W"))
    return controls


def coefficient_gaps(raw_targets, raw_paid, width_receipt, moment_receipt):
    v, b, c = 1024, 21, 20
    H = 64215200000000
    W0 = sum(raw_targets.values())
    need((W0, sum(raw_paid.values()), max(raw_targets), b, c) == (10928, 64620, 145, 21, 20),
         "raw selected invoice")
    W = W0 ** v
    L = b ** v
    M = max(raw_targets) ** v
    A = sum(count for rank, count in raw_targets.items() if rank <= b) ** v
    Qbar = paid_count_bound(raw_targets, raw_paid, v, b, c)
    hlo = (H - M.bit_length()) // L.bit_length()
    Xlo = (W.bit_length() - 1) + (hlo - 1) * (A.bit_length() - 1)
    env = width_receipt["envelope"]
    need((hlo, Xlo, env["height_lower"], env["x_lower"]) ==
         (14276389504, 188990844254451, 14276389504, 188990844254451),
         "PR5026 lower coefficient")
    Tbar = sum(rank * count for rank, count in raw_targets.items()) ** v + W * L
    hhi = (H - (M.bit_length() - 1)) // (L.bit_length() - 1)
    ratio = Tbar.bit_length() - (L.bit_length() - 1)
    X = (hhi + 1).bit_length() + Tbar.bit_length() + hhi * ratio
    moment = moment_receipt["coefficient"]
    need((hhi, X, moment["height_upper"], moment["X"], moment["K_over_N_strict_upper"]) ==
         (14279564152, 197115103572543, 14279564152, 197115103572543, "3070/1000"),
         "uniform moment coefficient")
    need(hlo >= 4, "height-1 window is disjoint from the top slab")
    need(145 * 441 == 63945 and 145 < 441 and 20 < 21, "window arithmetic")
    need(pow(145, v) < pow(441, v), "square window is nonempty at this power")
    log_cap = (Qbar * W).bit_length()
    need(Qbar >= W and log_cap < X, "height-1 count sits below the uniform charge")
    # Adding every height-1 logarithm still misses 2944/1000.
    lower_gap = 2944 * H * L - 1000 * (L - 1) * Xlo
    lower_mass = 1000 * log_cap * pow(63945 * 21, v)
    need(lower_gap > 0 and lower_mass.bit_length() <= H, "height-1 mass misses 2944/1000")
    # Deleting the whole uniform charge on those ranks still misses 3069/1000.
    upper_deficit = 1000 * X - 3069 * H
    upper_mass = 1000 * X * pow(63945, v)
    need(upper_deficit > 0 and upper_mass.bit_length() <= H, "height-1 removal misses 3069/1000")
    need(1000 * (L - 1) * Xlo > 2943 * L * H, "inherited lower endpoint")
    need(1000 * X < 3070 * H, "inherited upper endpoint")
    return {"H": H, "height_lower": hlo, "height_upper": hhi, "x_lower": Xlo, "X": X,
            "lower_endpoint": "2943/1000", "upper_endpoint": "3070/1000",
            "lower_thousandth_not_reached": "2944/1000",
            "upper_thousandth_not_reached": "3069/1000",
            "height1_log_cap_bits": log_cap,
            "lower_mass_bits": lower_mass.bit_length(),
            "upper_mass_bits": upper_mass.bit_length(),
            "selected_kappa_unchanged": "60403/20000000"}


def main():
    need(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    inputs = authenticated_inputs()
    module = ModuleType("authenticated_pr4436_flow")
    name = "research/direct-mixed-flow/flow.py"
    exec(compile(inputs[name], name, "exec"), module.__dict__)
    lattice = json.loads(inputs["research/joint-helper-lattice/RESULT.json"])
    width = json.loads(inputs["research/selected-complex-width-envelope/RESULT.json"])
    moment = json.loads(inputs["research/selected-truncated-source-envelope/RESULT.json"])
    raw_t = {int(k): n for k, n in lattice["targets"].items()}
    raw_p = {int(k): n for k, n in lattice["paid"].items()}
    targets, paid = literal_completion(raw_t, raw_p, 1, 21, 20)
    published = width["finite_checks"]["selected_v1_source_calibration"]
    for n, height, source_count in published:
        got = module.Flow(targets, paid, n).merged()
        need((got["height"], got["source_count"]) == (height, source_count),
             "published calibration row")
    small_caps, literals = small_profiles(module.Flow)
    slab = selected_slab(module.Flow, targets, paid)
    result = {"schema_version": 1, "evidence_level": "author-checked",
              "selected_kappa_unchanged": "60403/20000000",
              "height1": {"identity": "S = W*A(cap) + P*(W-A(cap))",
                          "small_profile_caps": small_caps, "literal_replays": literals,
                          "selected_v1": slab,
                          "negative_controls": negative_controls(module.Flow, targets, paid)},
              "endpoints": coefficient_gaps(raw_t, raw_p, width, moment)}
    need(authenticated_inputs() == inputs, "source bytes changed during replay")
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8")),
             "changed result receipt")
        print("PASS_HEIGHT1_TRUNCATED_SOURCE")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_HEIGHT1_TRUNCATED_SOURCE: " + str(exc), file=sys.stderr)
        sys.exit(1)
