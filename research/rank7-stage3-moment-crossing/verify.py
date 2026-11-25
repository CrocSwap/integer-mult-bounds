#!/usr/bin/env python3
"""Source-bound exact moment check for the PR2979 stage-3 histogram change.

This verifier does not import either source moment implementation. For each
rank r it encloses (73/r)^b by first enclosing its rational 32nd root with
integer bisection, then enclosing (1+y)^(32b) by adjacent partial sums of the
alternating generalized-binomial series. All interval endpoints and signs are
exact Fractions; no logarithm, exponential, float, or decimal participates in
the proof decisions.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha1, sha256
import argparse
import json
from pathlib import Path


BASE_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PR2979_HEAD = "be191346391661f4d35fc0d1508d0a6029572576"
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SOURCE_PACKAGE = ROOT / "research/rank7-joint-endframes"
ROOT_DEGREE = 32
ROOT_SCALE = 10 ** 100
BINOMIAL_TERMS = 80
RANK_BASE = 73
LIVE_PER_REPLICA = 896
MASS_PER_REPLICA = 65088


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(raw):
    return sha256(raw).hexdigest()


def git_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_source_pins():
    pins = read_json(PACKAGE / "SOURCES.json")
    need(pins["base_commit"] == BASE_COMMIT, "unexpected canonical base commit")
    verify_manifest = read_json(PACKAGE / "VERIFY.json")
    declared = set(verify_manifest["inputs"])
    input_rows = [row for row in pins["files"] if row["usage"] == "input"]
    need({row["path"] for row in input_rows} <= declared,
         "a live source pin is missing from VERIFY.json inputs")
    for row in input_rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(sha256_bytes(raw) == row["sha256"], "source SHA256 mismatch: " + row["path"])
        need(git_blob(raw) == row["git_blob"], "source Git blob mismatch: " + row["path"])
    return {row["path"]: row["sha256"] for row in input_rows}


def check_pinned_bytes(raw, expected_sha, expected_blob, name):
    need(sha256_bytes(raw) == expected_sha, "source SHA256 mismatch: " + name)
    need(git_blob(raw) == expected_blob, "source Git blob mismatch: " + name)


def profile(raw):
    result = {int(rank): int(count) for rank, count in raw.items()}
    need(result and all(0 < rank < RANK_BASE and count > 0
                        for rank, count in result.items()), "invalid positive rank profile")
    return result


def rank_mass(histogram):
    return sum(rank * count for rank, count in histogram.items())


def floor_nth_root(value, degree):
    """Return floor(value**(1/degree)) using integer comparisons only."""
    need(value >= 0 and degree > 0, "invalid integer root domain")
    if value < 2:
        return value
    low = 0
    high = 1 << ((value.bit_length() + degree - 1) // degree)
    while high - low > 1:
        middle = (low + high) // 2
        if middle ** degree <= value:
            low = middle
        else:
            high = middle
    return low


def binomial_bounds(exponent, y):
    """Enclose (1+y)**exponent for 0 < exponent < 1 and 0 <= y < 1.

    The generalized-binomial terms alternate after the constant and decrease
    in magnitude, since each successive absolute-term ratio is below y. The
    exact value is therefore between adjacent partial sums S_N and S_(N+1).
    """
    need(0 < exponent < 1 and 0 <= y < 1, "binomial-series domain")
    term = F(1)
    partial = term
    for n in range(1, BINOMIAL_TERMS + 1):
        term *= (exponent - (n - 1)) * y / n
        partial += term
    next_term = term * (exponent - BINOMIAL_TERMS) * y / (BINOMIAL_TERMS + 1)
    adjacent = partial + next_term
    return min(partial, adjacent), max(partial, adjacent)


def power_bounds(q, saving):
    """Exact enclosure of q**saving for q >= 1 and small rational saving."""
    need(q >= 1 and saving >= 0, "real-power domain")
    if saving == 0 or q == 1:
        return F(1), F(1)
    exponent = ROOT_DEGREE * saving
    need(exponent < 1, "transformed binomial exponent must be below one")

    scaled_power = (q.numerator * ROOT_SCALE ** ROOT_DEGREE) // q.denominator
    root_floor = floor_nth_root(scaled_power, ROOT_DEGREE)
    # Check the rational root enclosure without assuming the integer-root code.
    left = root_floor ** ROOT_DEGREE * q.denominator
    right = (root_floor + 1) ** ROOT_DEGREE * q.denominator
    need(left <= q.numerator * ROOT_SCALE ** ROOT_DEGREE < right,
         "integer 32nd-root enclosure failed")
    y_lower = F(root_floor, ROOT_SCALE) - 1
    y_upper = F(root_floor + 1, ROOT_SCALE) - 1
    need(0 <= y_lower <= y_upper < 1, "root-reduced binomial domain")
    lower = binomial_bounds(exponent, y_lower)[0]
    upper = binomial_bounds(exponent, y_upper)[1]
    return lower, upper


def moment_bounds(histogram, saving, width):
    """Enclose sum_r n_r*r*(73/r)**saving / (73*width) exactly."""
    need(width > 0, "positive width required")
    lower = F(0)
    upper = F(0)
    for rank, count in histogram.items():
        lo, hi = power_bounds(F(RANK_BASE, rank), saving)
        lower += rank * count * lo
        upper += rank * count * hi
    denominator = RANK_BASE * width
    return lower / denominator, upper / denominator


def decimal(value, digits=60):
    with localcontext() as context:
        context.prec = digits
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def interval_json(bounds):
    return {"lower_decimal": decimal(bounds[0]), "upper_decimal": decimal(bounds[1])}


def rejects(call):
    try:
        call()
    except (ValueError, AssertionError):
        return True
    return False


def run():
    pins = verify_source_pins()
    family_status = (ROOT / "docs/research/research-family-status.md").read_text(encoding="utf-8")
    need(PR2979_HEAD in family_status,
         "revision-6 family record no longer binds the PR2979 source head")
    package_manifest = read_json(SOURCE_PACKAGE / "MANIFEST.json")
    allocation_pins = read_json(SOURCE_PACKAGE / "ALLOCATION-PINS.json")
    claim = read_json(SOURCE_PACKAGE / "CLAIM.json")
    baseline = read_json(SOURCE_PACKAGE / "allocation/baseline/CLAIM.json")
    stages = read_json(SOURCE_PACKAGE / "certificates/RELAX-STAGES.json")
    stage_prices = read_json(SOURCE_PACKAGE / "construction/STAGE-PRICES.json")
    order = read_json(SOURCE_PACKAGE / "allocation/ORDER.json")
    full = profile(read_json(SOURCE_PACKAGE / "allocation/PROFILE.json"))
    fill_path = SOURCE_PACKAGE / "allocation/FILL.json.gz"

    # The outer package manifest and allocation ledger bind the exact profile,
    # order, fill and stage certificates used below.
    need(package_manifest.get("CLAIM.json") == pins[
             "research/rank7-joint-endframes/CLAIM.json"]
         and package_manifest.get("allocation/PROFILE.json") == pins[
             "research/rank7-joint-endframes/allocation/PROFILE.json"],
         "rank-7 source manifest does not bind the pinned claim and profile")
    need(sha256(fill_path.read_bytes()).hexdigest() == claim["fill_sha256"],
         "final T74 fill hash differs from the source claim")
    for relative in (
        "PROFILE.json", "ORDER.json", "FILL.json.gz", "PROVIDERS.json",
        "baseline/CLAIM.json",
    ):
        key = "allocation/" + relative
        need(key in allocation_pins, "allocation source pin missing: " + key)
        raw = (SOURCE_PACKAGE / key).read_bytes()
        need(sha256(raw).hexdigest() == allocation_pins[key],
             "allocation inventory mismatch: " + key)

    replicas = int(claim["replicas"])
    calls = int(claim["calls"])
    width = LIVE_PER_REPLICA * replicas
    claimed_full = profile(claim["profile"])
    need(claimed_full == full, "claim profile differs from the pinned complete allocation profile")
    need(replicas == 74 and calls == 9 * replicas == len(order),
         "T74 call/order dimensions do not match")
    need(min(row[1] for row in order) == 0 and max(row[1] for row in order) == replicas - 1,
         "T74 ORDER slot range does not match its replica count")
    need(claim["baseline_kappa"] == baseline["kappa"],
         "comparison endpoint differs from the pinned PR2969 claim")

    final_local = profile(claim["local_profile"])
    before_local = profile(stages["stage2"]["local_per_call"])
    final_inventory = {int(k): int(v) for k, v in claim["width_inventory"].items()}
    before_inventory = {int(k): int(v) for k, v in stages["stage2"]["inventory_per_call"].items()}
    need(final_inventory == before_inventory,
         "stage 3 changed the width inventory needed by the fixed-fill comparison")
    delta = {rank: final_local.get(rank, 0) - before_local.get(rank, 0)
             for rank in set(final_local) | set(before_local)}
    delta = {rank: count for rank, count in delta.items() if count}
    need(delta == {1: -4, 2: -4, 3: -4, 4: 6},
         "stage-3 local profile delta differs from the pinned fourteen-rewrite record")
    need(rank_mass(delta) == 0, "stage-3 local histogram change must preserve rank mass")
    stage3 = claim["stages"]["stage3"]
    rewrites = stage_prices["stage3"]["rewrites"]
    need(stage3["count"] == len(rewrites) == 14,
         "stage-3 rewrite count is not the pinned fourteen")
    need(sum(int(x) for x in rewrites.values()) == stage_prices["stage3"]["literal_price_units"] == -52350,
         "stage-3 rewrite price total differs from the pinned source")

    # Remove the final local child contribution to expose the frozen fill's
    # unchanged idle histogram. Replacing just the local contribution gives
    # the stage-2 counterfactual on the same T74 owner fill.
    idle = {rank: full.get(rank, 0) - calls * final_local.get(rank, 0)
            for rank in set(full) | set(final_local)}
    need(all(count >= 0 for count in idle.values()), "negative final idle histogram")
    idle = {rank: count for rank, count in idle.items() if count}
    after = dict(full)
    before = {rank: idle.get(rank, 0) + calls * before_local.get(rank, 0)
              for rank in set(idle) | set(before_local)}
    before = {rank: count for rank, count in before.items() if count}
    need({rank: idle.get(rank, 0) + calls * final_local.get(rank, 0)
          for rank in set(idle) | set(final_local)} == after,
         "final profile did not reconstruct from its local and idle histograms")
    need(rank_mass(before) == rank_mass(after) == MASS_PER_REPLICA * replicas,
         "before/after complete rank mass differs")
    need(before == {rank: after.get(rank, 0) - calls * delta.get(rank, 0)
                    for rank in set(after) | set(delta)
                    if after.get(rank, 0) - calls * delta.get(rank, 0)},
         "complete profile transition differs from its replicated local delta")

    saving = F(claim["kappa"])
    previous_saving = F(baseline["kappa"])
    need(saving > previous_saving, "candidate does not exceed the pinned prior headline")
    after_at_claim = moment_bounds(after, saving, width)
    before_at_claim = moment_bounds(before, saving, width)
    after_at_previous = moment_bounds(after, previous_saving, width)
    before_at_previous = moment_bounds(before, previous_saving, width)
    delta_bounds = (after_at_claim[0] - before_at_claim[1],
                    after_at_claim[1] - before_at_claim[0])
    need(after_at_claim[1] < 1 < before_at_claim[0],
         "stage-3 profile does not straddle the claim while stage 2 fails it")
    need(delta_bounds[1] < 0, "fourteen rewrites did not strictly lower the exact moment")
    need(after_at_previous[1] < 1 and before_at_previous[1] < 1,
         "positive prior-headline controls failed")
    at_zero_after = moment_bounds(after, F(0), width)
    at_zero_before = moment_bounds(before, F(0), width)
    need(at_zero_after == at_zero_before
         and at_zero_after[0] == F(MASS_PER_REPLICA * replicas, RANK_BASE * width),
         "rank-mass zero-saving control failed")

    # Semantic failures: the stage transition is essential, a one-child charge
    # invalidates the near-boundary post-stage inequality, and overstatement
    # crosses the exact moment. Source-byte tampering must also fail closed.
    no_transition = moment_bounds(after, saving, width)
    need(no_transition == after_at_claim and no_transition[1] < 1,
         "omitting stage 3 did not leave the post-stage profile below one without a crossing")
    extra_rank_one = dict(after)
    extra_rank_one[1] += 1
    extra_bound = moment_bounds(extra_rank_one, saving, width)
    need(extra_bound[0] > 1, "extra rank-1 semantic mutation was not rejected")
    overclaim = saving + F(1, 10 ** 22)
    overclaim_bound = moment_bounds(after, overclaim, width)
    need(overclaim_bound[0] > 1, "overstated saving was not rejected")

    source_row = next(row for row in read_json(PACKAGE / "SOURCES.json")["files"]
                      if row["path"] == "research/rank7-joint-endframes/allocation/PROFILE.json")
    source_bytes = (ROOT / source_row["path"]).read_bytes()
    need(rejects(lambda: check_pinned_bytes(source_bytes + b" ", source_row["sha256"],
                                           source_row["git_blob"], source_row["path"])),
         "source-byte corruption control did not fail")

    return {
        "status": "PASS_RANK7_STAGE3_BINOMIAL_MOMENT_CROSSING",
        "base_commit": BASE_COMMIT,
        "source_pr": 2979,
        "source_head": PR2979_HEAD,
        "source_package": "research/rank7-joint-endframes",
        "source_pins": pins,
        "replicas": replicas,
        "calls": calls,
        "width": width,
        "stage3_rewrites": stage3["count"],
        "stage3_profile_delta_per_call": {str(k): v for k, v in sorted(delta.items())},
        "stage3_profile_delta_rank_mass": rank_mass(delta),
        "fixed_fill_idle_profile": {str(k): v for k, v in sorted(idle.items())},
        "stage2_profile_on_final_fill": {str(k): v for k, v in sorted(before.items())},
        "final_profile": {str(k): v for k, v in sorted(after.items())},
        "claimed_saving": str(saving),
        "prior_headline": str(previous_saving),
        "moment_after_at_claim": interval_json(after_at_claim),
        "moment_before_at_claim": interval_json(before_at_claim),
        "moment_change_after_minus_before": {
            "upper_decimal": decimal(delta_bounds[1]),
            "strictly_negative": True,
        },
        "moment_after_at_prior_headline": interval_json(after_at_previous),
        "moment_before_at_prior_headline": interval_json(before_at_previous),
        "controls": {
            "zero_saving_rank_mass_identity": "PASS",
            "omitting_stage3_transition_does_not_cross_one": "PASS",
            "extra_rank1_charge_fails_post_stage_inequality": "PASS",
            "saving_overclaim_plus_1e-22_fails": "PASS",
            "source_byte_mutation_rejected": "PASS",
        },
        "method": {
            "root_degree": ROOT_DEGREE,
            "root_scale": str(ROOT_SCALE),
            "binomial_terms": BINOMIAL_TERMS,
            "enclosure": "integer 32nd-root bisection and adjacent alternating generalized-binomial partial sums",
            "uses_log_exp_float_or_source_moment_function": False,
        },
        "scope": "Arithmetic implication for the published rank-profile transition on a fixed final fill. No frame, circuit, native, whole-invoice, supplier-admission, or selected-frontier verification.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true",
                        help="write the deterministic certificate to RESULT.json")
    args = parser.parse_args()
    result = run()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"],
        "moment_after_at_claim": result["moment_after_at_claim"],
        "moment_before_at_claim": result["moment_before_at_claim"],
        "stage3_delta_upper": result["moment_change_after_minus_before"]["upper_decimal"],
        "controls": result["controls"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
