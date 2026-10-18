#!/usr/bin/env python3
"""Reconcile a historical family ceiling with a changed assembly conversion.

Standard library only; no predecessor code is imported or executed.
Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha1, sha256
from math import comb
from pathlib import Path
import argparse
import copy
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
CERTIFICATE = "certificates/prime-subset-limits.json"
SOURCE_PATHS = (
    CERTIFICATE,
    "docs/research/prime-subset-limits.md",
    "docs/research/core-limits.md",
    "docs/research/assembly-domain-audit.md",
    "scripts/audit_prime_subset_limits.py",
    "scripts/experiments/prime_subset_limits.py",
    "scripts/experiments/core_limits.py",
    "scripts/search_network.py",
    "research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py",
    "research/coordinated-frames-and-entrance-banks/arithmetic/shared_bridge.py",
    "research/complex-t37-owners/independent/all_t_bound.py",
    "research/complex-k492-owner-repair/vendor/multicold/engines/outer.py",
)
HISTORICAL_PIN_PATHS = {
    "docs/research/prime-subset-limits.md",
    "scripts/audit_prime_subset_limits.py",
    "scripts/experiments/prime_subset_limits.py",
    "scripts/experiments/core_limits.py",
    "scripts/search_network.py",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def same(actual, expected, label):
    # JSON canonical equality distinguishes booleans from integers and strings.
    require(canonical(actual) == canonical(expected), label + " differs")


def check_sources(root=ROOT, manifest=None):
    manifest = read_json(HERE / "SOURCES.json") if manifest is None else manifest
    same(manifest["base_commit"], BASE, "base commit")
    same(sorted(manifest["files"]), sorted(SOURCE_PATHS), "source inventory")
    for relative in SOURCE_PATHS:
        path = root / relative
        require(path.resolve().is_relative_to(root.resolve()), "source escapes root: " + relative)
        require(path.is_file(), "missing source: " + relative)
        data = path.read_bytes()
        pin = manifest["files"][relative]
        require(sha256(data).hexdigest() == pin["sha256"], "source digest: " + relative)
        git_blob = sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(git_blob == pin["git_blob"], "Git blob differs: " + relative)
    return manifest


def prime_powers(limit):
    """Sieve primes, then generate their powers (independent of trial division)."""
    sieve = [True] * (limit + 1)
    sieve[:2] = [False, False]
    result = set()
    for p in range(2, limit + 1):
        if not sieve[p]:
            continue
        for multiple in range(p * p, limit + 1, p):
            sieve[multiple] = False
        power = p
        while power <= limit:
            result.add(power)
            power *= p
    return sorted(result)


def log_unit_bounds(x, terms=96):
    """ln(x) = sum z**j/j, z=1-1/x, with a geometric remainder.

    This is not the predecessor's atanh series. For 1<=x<=2, 0<=z<=1/2.
    The omitted tail is at most z**(N+1)/((N+1)*(1-z)).
    """
    require(isinstance(x, Q) and 1 <= x <= 2, "log interval domain")
    require(type(terms) is int and terms > 0, "positive log term count")
    z = 1 - 1 / x
    term, total = z, Q(0)
    for j in range(1, terms + 1):
        total += term / j
        term *= z
    return total, total + term / ((terms + 1) * (1 - z))


@lru_cache(maxsize=None)
def log_integer_bounds(n):
    require(type(n) is int and n >= 2, "integer log domain")
    exponent = n.bit_length() - 1
    l2, u2 = log_unit_bounds(Q(2))
    lr, ur = log_unit_bounds(Q(n, 2**exponent))
    return exponent * l2 + lr, exponent * u2 + ur


def historical_log_lower(n):
    """Reconstruct the archived 24-term rational exactly, without imports."""
    def partial(x):
        z = (x - 1) / (x + 1)
        power, total = z, Q(0)
        for denominator in range(1, 48, 2):
            total += 2 * power / denominator
            power *= z * z
        return total
    exponent = n.bit_length() - 1
    return exponent * partial(Q(2)) + partial(Q(n, 2**exponent))


def family(q, h):
    k, j = 2 * q - 1, q - 1
    n, r, multiplicity = comb(h, k), comb(h, j), comb(k, j)
    deficit = n - 6 * r * h
    if deficit <= 0:
        return None
    require(h >= 3 * q and multiplicity >= 3, "partial-output floor domain")
    side = 2 * multiplicity * n
    eta = Q(deficit, 2 * h**3 * (n + side + r))
    require(0 < eta < Q(1, 14 * h**3), "uniform family tail premise")
    lo, hi = log_integer_bounds(h**3)
    numerator = eta / (1 - eta)
    # A is the old optimistic envelope, not an attained supplier saving.
    return dict(n=n, r=r, multiplicity=multiplicity, side=side, eta=eta,
                lower=numerator / hi, upper=numerator / lo,
                historical_upper=numerator / historical_log_lower(h**3))


def interval_json(lo, hi):
    """Outward rounding produces short, exact rational receipt endpoints."""
    scale = 10**36
    a = (lo * scale).numerator // (lo * scale).denominator
    b = -(-(hi * scale).numerator // (hi * scale).denominator)
    return {"lower": str(Q(a, scale)), "upper": str(Q(b, scale))}


def reconcile(certificate):
    env = certificate["envelope"]
    require(env["all_prime_powers_and_ground_sizes_excluded"] is True, "historical exclusion flag")
    require(Q(env["target"]) == Q(1, 2**26), "historical target")
    tail = env["tail_dimension_exclusion"]
    require(type(tail["first_excluded_dimension"]) is int and
            tail["first_excluded_dimension"] == 65, "historical cutoff")
    domain = [(q, h) for q in prime_powers(32) for h in range(2 * q - 1, 65)]
    rows = env["cases"]
    require(type(rows) is list and len(rows) == len(domain) == 626, "finite coverage count")
    positives, checked = {}, []
    for row, (q, h) in zip(rows, domain):
        actual = family(q, h)
        expected = dict(q=q, h=h, positive_deficit=actual is not None)
        if actual is not None:
            a = actual
            expected.update(n=a["n"], r=a["r"], outputs_per_label=a["multiplicity"],
                            side_role_floor=a["side"], eta_upper=str(a["eta"]),
                            bit_saving_upper=str(a["historical_upper"]),
                            kappa_upper=str(a["historical_upper"] / 5))
            positives[q, h] = a
            checked.append(dict(q=q, h=h, **interval_json(a["lower"], a["upper"])))
        same(row, expected, "finite row " + str((q, h)))
    winner = max(positives, key=lambda pair: positives[pair]["lower"])
    best = positives[winner]
    require(winner == (3, 29), "finite winner")
    require(all(best["lower"] > value["upper"] for pair, value in positives.items()
                if pair != winner), "finite maximum not separated")
    same(env["best_finite_upper"], rows[domain.index(winner)], "historical winner record")
    # Old generic 4*h^3 bound is only enough after the old /5 conversion.
    lo65, hi65 = log_integer_bounds(65**3)
    generic_tail = Q(1, 4 * 65**3 - 1) / lo65
    tailored_tail = Q(1, 14 * 65**3 - 1) / lo65
    require(generic_tail / 5 < Q(1, 2**26), "historical tail exclusion")
    require(Q(1, 4 * 65**3 - 1) / hi65 > Q(1, 2**24),
            "tail-gap negative control premise")
    require(tailored_tail < best["lower"], "tail not below finite envelope")
    balanced_lo = best["lower"] / (1 + best["lower"])
    balanced_hi = best["upper"] / (1 + best["upper"])
    require(best["historical_upper"] / 5 < Q(1, 2**26), "old exclusion")
    require(Q(1, 2**25) < balanced_lo < balanced_hi < Q(1, 2**24), "new exclusion bracket")
    # A positive reduced-inequality control, emphatically not a construction.
    a, backoff, target = Q(3, 10**8), Q(1, 10**12), Q(1, 2**25)
    log_rate_lo, _ = log_unit_bounds(1 / (1 - best["eta"]))
    ideal_rate_lower = log_rate_lo / log_integer_bounds(29**3)[1]
    q_eff = a * (1 - 2 * backoff)
    epsilon = (1 - backoff) / (1 + q_eff)
    gain = epsilon * q_eff
    require(a < ideal_rate_lower, "diagnostic rate exceeds ideal relaxed rate")
    require(target < gain and target < 1 - epsilon, "balanced diagnostic margins")
    require(1 - epsilon - gain == backoff, "balanced diagnostic identity")
    require(a / 5 < target, "old conversion must reject diagnostic target")
    return dict(
        status="PASS_PRIME_SUBSET_ASSEMBLY_SCOPE_NO_NEW_KAPPA", base_commit=BASE,
        seed=95, finite_case_count=len(rows), positive_case_count=len(positives),
        finite_cases_by_q={str(q): sum(1 for x, _ in domain if x == q) for q in prime_powers(32)},
        checked_enclosures_sha256=sha256(canonical(checked).encode("ascii")).hexdigest(),
        winner=dict(q=3, h=29, n=best["n"], r=best["r"], side_role_floor=best["side"],
                    eta_upper=str(best["eta"]), bit_envelope=interval_json(best["lower"], best["upper"]),
                    balanced_envelope=interval_json(balanced_lo, balanced_hi)),
        tail=dict(first_h=65, factor=14, bound_at_65=str(interval_json(Q(0), tailored_tail)["upper"]),
                  generic_factor4_bound_at_65=str(interval_json(Q(0), generic_tail)["upper"]),
                  decreasing_for_all_h_at_least_65=True, below_finite_winner=True),
        conversions=dict(historical="A/5", balanced="A/(1+A)",
                         historical_excludes_2_to_minus26=True,
                         transferred_ceiling_excludes_2_to_minus24=True,
                         transferred_ceiling_excludes_2_to_minus25=False,
                         transferred_ceiling_excludes_2_to_minus26=False),
        reduced_diagnostic=dict(scope="TWO BALANCED MARGINS ONLY; NO SUPPLIER OR BRIDGE ADMISSION",
                                a=str(a), backoff=str(backoff), target=str(target),
                                epsilon=str(epsilon), gain=str(gain),
                                gain_slack=str(gain-target), normalization_slack=str(1-epsilon-target),
                                ideal_rate_lower=interval_json(ideal_rate_lower, ideal_rate_lower)["lower"]),
    )


def negative_controls(certificate):
    controls = []
    def rejects(name, mutate):
        changed = copy.deepcopy(certificate)
        mutate(changed)
        try:
            reconcile(changed)
        except (ValueError, KeyError, TypeError):
            controls.append(name)
        else:
            raise ValueError("accepted negative control: " + name)
    rejects("missing_last_finite_case", lambda x: x["envelope"]["cases"].pop())
    rejects("duplicate_case", lambda x: x["envelope"]["cases"].__setitem__(1, x["envelope"]["cases"][0]))
    rejects("non_prime_power_substitution", lambda x: x["envelope"]["cases"][0].__setitem__("q", 6))
    rejects("missing_divisor_five", lambda x: x["envelope"]["best_finite_upper"].__setitem__(
        "kappa_upper", x["envelope"]["best_finite_upper"]["bit_saving_upper"]))
    rejects("incorrect_cutoff", lambda x: x["envelope"]["tail_dimension_exclusion"].__setitem__("first_excluded_dimension", 64))
    rejects("boolean_dimension", lambda x: x["envelope"]["cases"][0].__setitem__("h", True))
    rejects("unproved_stronger_target", lambda x: x["envelope"].__setitem__("target", str(Q(1, 2**27))))
    positive_index = next(i for i, r in enumerate(certificate["envelope"]["cases"]) if r["positive_deficit"])
    rejects("underpriced_side_floor", lambda x: x["envelope"]["cases"][positive_index].__setitem__("side_role_floor", 0))
    return controls


def calculate(root=ROOT):
    manifest = check_sources(root)
    certificate = read_json(root / CERTIFICATE)
    same(sorted(certificate["source_sha256"]), sorted(HISTORICAL_PIN_PATHS), "historical pin set")
    for path, digest in certificate["source_sha256"].items():
        same(digest, manifest["files"][path]["sha256"], "historical pin " + path)
    result = reconcile(certificate)
    result["negative_controls"] = negative_controls(certificate)
    result["source_count"] = len(SOURCE_PATHS)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    result = calculate()
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        same(result, read_json(HERE / "RESULT.json"), "committed receipt")
    print(result["status"] + " cases=626 controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
