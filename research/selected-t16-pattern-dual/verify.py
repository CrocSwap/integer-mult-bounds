#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact selected-T16 pattern LP certificate; no optimizer or repo-code imports.

Hanson Sun, with substantial OpenAI Codex assistance. See README for the
concavity proof, inherited source model, exclusions and predecessor credit.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from math import isqrt
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/complex-t16-rare-pattern-exchanges/data/"
AUDIT = "research/community-frontier1094-audit/"
WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_inputs():
    """Historical pointer is Git provenance; the named finite inputs are live pins."""
    pins = json.loads((HERE / "SOURCES.json").read_text())
    decoded = {}
    for entry in pins["files"]:
        path = entry["path"]
        blob = subprocess.check_output(["git", "cat-file", "blob", entry["git_blob"]], cwd=ROOT)
        need(sha(blob) == entry["sha256"], "Git source pin: " + path)
        if entry["usage"] == "input":
            need((ROOT / path).read_bytes() == blob, "source drift: " + path)
        if path.endswith((".json", ".gz")):
            decoded[path] = json.loads(gzip.decompress(blob) if path.endswith(".gz") else blob)
    selected = decoded["certificates/selected-result.json"]
    need(selected["certificate"] == AUDIT + "ASSEMBLY.json", "selected certificate path")
    need(selected["source_manifest"] == AUDIT + "SELECTED-SOURCE.json", "selected manifest path")
    need(sha((ROOT / selected["certificate"]).read_bytes()) == selected["certificate_sha256"],
         "selected certificate digest")
    manifest = decoded[selected["source_manifest"]]["files"]
    for name in ("PLAN.json", "SPEC.json", "OWNERS.json.gz"):
        path = PREFIX + name
        need(sha((ROOT / path).read_bytes()) == manifest[path], "selected input binding: " + path)
    spec = decoded[PREFIX + "SPEC.json"]
    for name, key in (("PLAN.json", "plan_sha256"), ("OWNERS.json.gz", "owners_sha256")):
        need(sha((ROOT / (PREFIX + name)).read_bytes()) == spec["data"][key], "SPEC input binding")
    return decoded


def source_model(plan, spec, owners):
    """Recount counts/widths and the positive owner fixture, not physical operators."""
    need(plan["M"] == 73 and plan["T"] == 16 and plan["L"] == 9, "fixed template")
    need(set(plan["provider_registry"]) == {"gauge44"}, "single fixed provider")
    ports = len(plan["provider_registry"]["gauge44"]["ports"])
    need(ports == 112 and plan["live"] == 14336, "fixed family stock")
    order = [tuple(call) for call in plan["order"]]
    need(len(order) == 144 and set(order) == {(s, t) for s in range(9) for t in range(16)},
         "complete call set")
    widths = {(row["stage"], row["replica"]): row["widths"] for row in plan["per_call_widths"]}
    need(len(plan["per_call_widths"]) == len(widths) == len(order) and set(widths) == set(order),
         "width call set")
    provider = spec["providers"]["gauge44"]
    inventory = {int(w): n for w, n in provider["inventory"].items()}
    need(set(inventory) == set(WIDTHS), "helper alphabet")
    for values in widths.values():
        need(all(type(w) is int and w > 0 for w in values), "helper width domain")
        need(Counter(values) == inventory, "per-call inventory")
    helper_counts = Counter(w for values in widths.values() for w in values)
    windows, capacity_counts = {}, Counter()
    for key, (capacity, times) in plan["windows"].items():
        owner, child = map(int, key.split(","))
        need(0 <= owner < 16 and capacity in CAPS and type(capacity) is int, "capacity domain")
        need(times and len(times) == len(set(times)) and all(type(t) is int and 0 <= t < 144 for t in times),
             "window domain")
        windows[owner, child] = (capacity, set(times))
        capacity_counts[capacity] += ports
    need(len(windows) == 288 and set(capacity_counts) == set(CAPS), "window inventory")
    bins = defaultdict(list)
    seen = set()
    for row in owners:
        stage, replica, helper = row["stage"], row["replica"], row["helper"]
        call = stage, replica
        need(call in widths and type(helper) is int and 0 <= helper < len(widths[call]), "owner helper")
        key = stage, replica, helper
        need(key not in seen, "duplicate helper")
        seen.add(key)
        need(row["width"] == widths[call][helper], "owner width")
        owner_key = row["owner_replica"], row["child"]
        need(owner_key in windows, "owner window")
        need(type(row["time"]) is int and 0 <= row["time"] < len(order)
             and order[row["time"]] == call and row["time"] in windows[owner_key][1], "owner timing")
        need(type(row["port"]) is int and 0 <= row["port"] < ports, "owner port")
        need(row["copy"] == row["owner_replica"] * ports + row["port"], "owner copy")
        need(type(row["offset"]) is int and row["offset"] >= 0, "owner offset")
        bins[(*owner_key, row["port"])].append((row["offset"], row["width"]))
    need(len(seen) == sum(helper_counts.values()), "complete helper set")
    idle = Counter()
    for owner_key, (capacity, _) in windows.items():
        for port in range(ports):
            used = 0
            for offset, width in sorted(bins[(*owner_key, port)]):
                need(offset == used, "owner prefix")
                used += width
            need(used <= capacity, "owner capacity")
            if used < capacity:
                idle[capacity - used] += 1
    local = {int(r): n for r, n in provider["expected_profile"].items()}
    need(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "fixed paid local profile")
    full = Counter({r: len(order) * n for r, n in local.items()}) + idle
    expected_idle = {int(r): n for r, n in spec["expected"]["idle_remainder_profile"].items()}
    need(idle == expected_idle, "selected idle recount")
    need(full == {int(r): n for r, n in plan["profile"].items()}, "selected profile recount")
    idle_mass = sum(c * n for c, n in capacity_counts.items()) - sum(w * n for w, n in helper_counts.items())
    need(sum(r * n for r, n in idle.items()) == idle_mass == 237024, "idle mass")
    need(sum(r * n for r, n in full.items()) == 73 * plan["live"] - plan["deficit"] == 1041408,
         "selected rank conservation")
    return dict(capacities=capacity_counts, helpers=helper_counts, local=local,
                selected_idle=idle, selected_profile=full, calls=len(order), live=plan["live"],
                m=plan["M"], idle_mass=idle_mass, owners=len(owners))


def patterns(capacity, widths=WIDTHS):
    """Every nonnegative integer count vector whose total width fits the bin."""
    def walk(index, remaining, counts):
        if index == len(widths):
            yield tuple(counts), remaining
        else:
            for count in range(remaining // widths[index] + 1):
                yield from walk(index + 1, remaining - count * widths[index], counts + [count])
    yield from walk(0, capacity, [])


def ceil_sqrt(value):
    root = isqrt(value)
    return root + (root * root != value)


@lru_cache(maxsize=None)
def half_powers(rank, exponent_bits, fraction_bits):
    scale = 1 << fraction_bits
    lo = hi = rank * scale
    chain = []
    for _ in range(exponent_bits):
        lo, hi = isqrt(lo * scale), ceil_sqrt(hi * scale)
        chain.append((lo, hi))
    return tuple(chain)


def power_interval(rank, exponent, exponent_bits=160, fraction_bits=256):
    """Enclose rank**exponent by outward integer square roots and products.

    Bracket the rational exponent on a dyadic grid, then multiply its binary
    half-power factors. No logarithms, exp, floats, or predecessor engines.
    """
    need(type(rank) is int and rank >= 0 and 0 < exponent <= 1, "power domain")
    need(type(exponent_bits) is int and exponent_bits > 0 and type(fraction_bits) is int
         and fraction_bits > 0, "precision domain")
    if rank in (0, 1) or exponent == 1:
        return Q(rank), Q(rank)
    scale, denominator = 1 << fraction_bits, 1 << exponent_bits
    lower_index = exponent.numerator * denominator // exponent.denominator
    upper_index = -(-exponent.numerator * denominator // exponent.denominator)
    chain = half_powers(rank, exponent_bits, fraction_bits)

    def dyadic(index):
        if index == denominator:
            return rank * scale, rank * scale
        lo = hi = scale
        for i, (left, right) in enumerate(chain, 1):
            if index & (1 << (exponent_bits - i)):
                lo = lo * left // scale
                hi = (hi * right + scale - 1) // scale
        return lo, hi

    return Q(dyadic(lower_index)[0], scale), Q(dyadic(upper_index)[1], scale)


def linear_interval(terms, exponent, **precision):
    lo = hi = Q(0)
    for rank, coefficient in terms.items():
        left, right = power_interval(rank, exponent, **precision)
        lo += coefficient * (left if coefficient >= 0 else right)
        hi += coefficient * (right if coefficient >= 0 else left)
    return lo, hi


def check_certificate(cert, model):
    need(tuple(cert["widths"]) == WIDTHS and tuple(cert["capacities"]) == CAPS, "certificate alphabet")
    need(cert["valid_saving_interval"] == ["0", "1/2"], "uniform interval")
    denominator = cert["dual_denominator"]
    need(type(denominator) is int and denominator > 0, "dual denominator")
    arrays = [cert["dual_constant_numerators"], cert["dual_power48_numerators"]]
    need(all(len(row) == 9 and all(type(x) is int for x in row) for row in arrays), "dual shape")
    constants, powers = [[Q(x, denominator) for x in row] for row in arrays]
    rhs = [model["capacities"][c] for c in CAPS] + [model["helpers"][w] for w in WIDTHS]

    def coefficients(capacity, counts):
        column = [int(capacity == c) for c in CAPS] + list(counts)
        return column, sum(x*y for x, y in zip(column, constants)), sum(x*y for x, y in zip(column, powers))

    total = exact = 0
    smallest = None
    for capacity in CAPS:
        for counts, residual in patterns(capacity):
            _, A, B = coefficients(capacity, counts)
            need(A + 48 * B == residual, "dual mass endpoint")
            total += 1
            if (residual, A, B) in ((0, 0, 0), (1, 1, 0), (48, 0, 1)):
                exact += 1
                continue
            # At p=1/2, bound sqrt(r)-A-B*sqrt(48) with directed intervals.
            terms = defaultdict(Q)
            terms[residual] += 1
            terms[1] -= A
            terms[48] -= B
            gap = linear_interval(terms, Q(1, 2))
            need(gap[0] > 0, "dual square-root endpoint")
            smallest = gap[0] if smallest is None else min(smallest, gap[0])
    need(total == 1163, "pattern enumeration")
    used = [Q(0)] * len(rhs)
    idle = defaultdict(Q)
    seen = set()
    for row in cert["primal_patterns"]:
        capacity, counts = row["capacity"], row["counts"]
        need(capacity in CAPS and len(counts) == len(WIDTHS)
             and all(type(n) is int and n >= 0 for n in counts), "primal pattern domain")
        key = capacity, tuple(counts)
        need(key not in seen, "duplicate primal pattern")
        seen.add(key)
        residual = capacity - sum(w*n for w, n in zip(WIDTHS, counts))
        need(residual >= 0 and row["residual"] == residual, "primal capacity")
        multiplicity = Q(row["multiplicity"])
        need(multiplicity > 0, "primal nonnegative")
        column, A, B = coefficients(capacity, counts)
        need((residual, A, B) in ((0, 0, 0), (1, 1, 0), (48, 0, 1)), "complementary equality")
        used = [x + multiplicity*y for x, y in zip(used, column)]
        if residual:
            idle[residual] += multiplicity
    need(used == rhs, "primal inventories")
    dual_value = (sum(x*y for x, y in zip(rhs, constants)), sum(x*y for x, y in zip(rhs, powers)))
    need(dict(idle) == {1: dual_value[0], 48: dual_value[1]}, "primal dual equality")
    need(sum(r*n for r, n in idle.items()) == model["idle_mass"], "relaxation mass")
    # On the 20 symbolic tight patterns, the constant dual coefficient counts
    # rank-1 residuals. Its forced fractional value excludes integer attainment.
    need(dual_value[0].denominator > 1, "strict integer nonattainment")
    return dict(idle=idle, patterns=total, symbolic_equalities=exact,
                strict_half_endpoint=total-exact, minimum_strict_half_gap=smallest)


def complete_profile(model, idle):
    profile = defaultdict(Q, {r: Q(model["calls"] * n) for r, n in model["local"].items()})
    for r, n in idle.items():
        profile[r] += n
    return dict(profile)


def moment_gap(profile, saving, m=73, live=14336, **precision):
    need(0 <= saving < 1, "saving domain")
    need(m > 0 and live > 0 and all(type(r) is int and 0 < r < m and n >= 0 for r, n in profile.items()),
         "moment profile")
    terms = dict(profile)
    terms[m] = -Q(live)
    return linear_interval(terms, 1-saving, **precision)


def root_bracket(profile):
    grid = 10**15
    lo, hi = 0, grid // 100
    need(moment_gap(profile, Q(lo, grid))[1] < 0, "root lower endpoint")
    need(moment_gap(profile, Q(hi, grid))[0] > 0, "root upper endpoint")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        left, right = moment_gap(profile, Q(mid, grid))
        if right < 0:
            lo = mid
        elif left > 0:
            hi = mid
        else:
            raise ValueError("unresolved root interval")
    return Q(lo, grid), Q(hi, grid)


def check_predecessor(cert, predecessor, profile):
    """Bind the independently derived certificate to Ali Romman's prior optimum.

    The numerical optimum and nine-pattern basis are predecessor results.
    Our uniform square-root proof and exact implementation are separate.
    """
    need(predecessor["replicas"] == 37, "predecessor replica count")
    old = {(row["capacity"], tuple(row["width_counts"])): Q(16 * row["bins"], 37)
           for row in predecessor["packing"]}
    new = {(row["capacity"], tuple(row["counts"])): Q(row["multiplicity"])
           for row in cert["primal_patterns"]}
    need(old == new, "predecessor pattern scaling")
    signed_prices = ([predecessor["capacity_bonuses"][str(c)] for c in CAPS]
                     + [predecessor["width_prices"][str(w)] for w in WIDTHS])
    masses = [*CAPS, *(-w for w in WIDTHS)]
    A = [Q(48*s + 13*r, 925) for s, r in zip(signed_prices, masses)]
    B = [(r-a)/48 for r, a in zip(masses, A)]
    need(A == [Q(n, cert["dual_denominator"]) for n in cert["dual_constant_numerators"]]
         and B == [Q(n, cert["dual_denominator"]) for n in cert["dual_power48_numerators"]],
         "predecessor dual reconciliation")
    lo, hi = map(Q, predecessor["root_interval"])
    need(0 < lo < hi < Q(1, 2), "predecessor root domain")
    need(moment_gap(profile, lo)[1] < 0 and moment_gap(profile, hi)[0] > 0,
         "predecessor strict root signs")
    return lo, hi


def controls(cert, model, plan, spec, owners):
    rejected = []

    def reject(name, action, message):
        try:
            action()
        except ValueError as exc:
            need(str(exc) == message, "unexpected control failure: " + name + ": " + str(exc))
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    mutant = deepcopy(cert)
    mutant["dual_constant_numerators"][4] += 1
    reject("wrong dual weight", lambda: check_certificate(mutant, model), "dual mass endpoint")
    # Preserve the p=1 mass identity; overprice the empty48 bin at p=1/2.
    mutant = deepcopy(cert)
    mutant["dual_constant_numerators"][3] += 48
    mutant["dual_power48_numerators"][3] -= 1
    reject("mass-preserving unsound dual", lambda: check_certificate(mutant, model), "dual square-root endpoint")
    mutant = deepcopy(cert)
    mutant["primal_patterns"][0]["multiplicity"] = "10751"
    reject("missing bin", lambda: check_certificate(mutant, model), "primal inventories")
    mutant = deepcopy(cert)
    mutant["primal_patterns"][-1]["counts"][-1] += 1
    reject("overfull primal pattern", lambda: check_certificate(mutant, model), "primal capacity")
    mutant = deepcopy(cert)
    mutant["primal_patterns"][0]["multiplicity"] = "-1"
    reject("negative multiplicity", lambda: check_certificate(mutant, model), "primal nonnegative")
    mutant = deepcopy(cert)
    mutant["valid_saving_interval"] = ["0", "1"]
    reject("unproved exponent range", lambda: check_certificate(mutant, model), "uniform interval")
    mutant = deepcopy(model)
    mutant["helpers"][4] -= 2
    mutant["helpers"][8] += 1
    reject("mass-preserving helper substitution", lambda: check_certificate(cert, mutant), "primal inventories")
    bad_row = dict(owners[0], width=owners[0]["width"] - 1)
    reject("owner width undercharge", lambda: source_model(plan, spec, [bad_row, *owners[1:]]), "owner width")
    bad_row = dict(owners[0], offset=owners[0]["offset"] + 1)
    reject("owner prefix gap", lambda: source_model(plan, spec, [bad_row, *owners[1:]]), "owner prefix")
    reject("duplicate owner helper", lambda: source_model(plan, spec, [owners[0], *owners]), "duplicate helper")
    reject("rank outside moment domain", lambda: moment_gap({73: 1}, Q(1, 100)), "moment profile")
    return rejected


def run():
    inputs = load_inputs()
    plan, spec, owners = [inputs[PREFIX + name] for name in ("PLAN.json", "SPEC.json", "OWNERS.json.gz")]
    model = source_model(plan, spec, owners)
    assembly, replay = inputs[AUDIT + "ASSEMBLY.json"], inputs[AUDIT + "REPLAY.json"]
    for source in (assembly, replay):
        need(model["selected_profile"] == {int(r): n for r, n in source["complex_profile"].items()},
             "assembly profile binding")
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    proof = check_certificate(cert, model)
    profile = complete_profile(model, proof["idle"])
    coarse_lo, coarse_hi = root_bracket(profile)
    predecessor = inputs["research/r480-owner-optimum/CERTIFICATE.json"]
    lo, hi = check_predecessor(cert, predecessor, profile)
    need(coarse_lo < lo < hi < coarse_hi, "independent coarse root bracket")
    selected_a = Q(assembly["complex_lower"])
    need(moment_gap(model["selected_profile"], selected_a)[1] < 0, "selected positive moment")
    need(moment_gap(model["selected_profile"], selected_a + Q(1, 10**24))[0] > 0,
         "selected next-grid rejection")
    need(selected_a < lo < hi < Q(1681977435447, 10**15), "strict bound improvement")
    need(moment_gap(model["selected_profile"], hi)[0] > 0, "selected fails at cap")
    strict_controls = controls(cert, model, plan, spec, owners)
    for endpoint in (lo, hi):
        coarse = moment_gap(profile, endpoint)
        fine = moment_gap(profile, endpoint, exponent_bits=192, fraction_bits=320)
        need(coarse[0] <= fine[0] <= fine[1] <= coarse[1], "precision nesting")
    kappa_cap = hi / (1 + hi)
    selected_kappa = Q(assembly["kappa"])
    return {
        "scope": "Independent verification and uniform square-root proof of the prior R480 optimum on 0<a<=1/2, bound to selected T16 inputs; no new numerical optimum or physical construction.",
        "capacity_inventory": dict(sorted(model["capacities"].items())),
        "helper_inventory": dict(sorted(model["helpers"].items())),
        "owner_rows_recounted": model["owners"], "calls": model["calls"], "live": model["live"],
        "local_profile_per_call": model["local"], "selected_idle_recount": dict(sorted(model["selected_idle"].items())),
        "idle_mass": model["idle_mass"], "patterns_checked": proof["patterns"],
        "symbolically_tight_patterns": proof["symbolic_equalities"],
        "strict_square_root_endpoint_patterns": proof["strict_half_endpoint"],
        "minimum_strict_square_root_gap_lower": str(proof["minimum_strict_half_gap"]),
        "optimal_fractional_idle_histogram": {str(r): str(n) for r, n in sorted(proof["idle"].items())},
        "integer_attainment": "Impossible at T16: optimal support forces 89952/37 rank-1 residuals; the prior T37 attainment is outside this fixed-replica claim.",
        "complete_relaxed_histogram": {str(r): str(n) for r, n in sorted(profile.items())},
        "primitive_root_bracket": [str(lo), str(hi)],
        "independent_coarse_root_bracket": [str(coarse_lo), str(coarse_hi)],
        "predecessor_reconciliation": "PR1129: same nine patterns scaled from T37 to T16; dual is an exact transform of the prior signed prices; finer prior root signs independently rechecked.",
        "root_endpoint_unnormalized_gaps": [[str(x) for x in moment_gap(profile, a)] for a in (lo, hi)],
        "balanced_kappa_upper": str(kappa_cap), "selected_kappa": str(selected_kappa),
        "relative_headroom_upper": str(kappa_cap / selected_kappa - 1),
        "semantic_controls_rejected": strict_controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's RESULT.json")
    args = parser.parse_args()
    payload = json.loads(json.dumps(run(), sort_keys=True))
    result_path = HERE / "RESULT.json"
    if args.write:
        result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        need(payload == json.loads(result_path.read_text()), "result mismatch")
    print("PASS_SELECTED_T16_PATTERN_DUAL", "patterns=" + str(payload["patterns_checked"]),
          "controls=" + str(len(payload["semantic_controls_rejected"])),
          "root=" + str(payload["primitive_root_bracket"]))


if __name__ == "__main__":
    main()
