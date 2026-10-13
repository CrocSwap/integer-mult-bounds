#!/usr/bin/env python3
"""Separately structured check of EXPECTED.json; no import of verify.py.

Uses dynamic programming for bins, synchronous Bellman-Ford for the residue
graph, and the other pinned retained rational engine (Mercator). The engine
is reused, not a newly independent transcendental implementation. Its two
called functions have their domain requirements checked explicitly here,
so this checker supports Python -I -O -B. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]
PRECISION = 10**24
ENDPOINT = Fraction("0.001664727258740678855773")
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
MERCATOR = "research/complex-k492-owner-repair/vendor/multicold/engines/moment.py"
MERCATOR_SHA256 = "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482"
HELPERS = ((4, -1), (5, -20), (7, -8), (8, -2), (9, 4))
BIN_TYPES = ((8, 672, 2), (16, 448, 4), (32, 448, 8), (48, 448, -13))


def check(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def bin_dynamic_program():
    """Optimal exact-fill score and a separate unbounded coin-change count."""
    score = [None] * 49
    score[0] = 0
    for filled in range(1, 49):
        candidates = [score[filled - width] + price
                      for width, price in HELPERS
                      if filled >= width and score[filled - width] is not None]
        if candidates:
            score[filled] = max(candidates)
    ways = [0] * 49
    ways[0] = 1
    for width, _ in HELPERS:
        for filled in range(width, 49):
            ways[filled] += ways[filled - width]
    residual_prices = {}
    pattern_count = 0
    for capacity, _, bonus in BIN_TYPES:
        pattern_count += sum(ways[:capacity + 1])
        check((48 * bonus + 13 * capacity) % 25 == 0, "bonus lattice")
        for filled in range(capacity + 1):
            check(bool(ways[filled]) == (score[filled] is not None), "DP support agreement")
            if score[filled] is not None:
                residual = capacity - filled
                proposal = bonus + score[filled]
                if residual not in residual_prices or proposal > residual_prices[residual]:
                    residual_prices[residual] = proposal
    check(pattern_count == 1163, "DP count of legal bin patterns")
    for width, price in HELPERS:
        check((48 * price - 13 * width) % 25 == 0, "helper lattice")
    check(residual_prices[0] == 0 and residual_prices[1] == 19 and residual_prices[48] == -13,
          "zero, rank-one and maximal residual prices")
    check(48 * residual_prices[1] + 13 == 925
          and 48 * residual_prices[2] + 26 == 650, "support and sharp-witness credits")
    return residual_prices


def read_phi(ranks):
    engine_file = REPOSITORY / MERCATOR
    check(hashlib.sha256(engine_file.read_bytes()).hexdigest() == MERCATOR_SHA256,
          "pinned Mercator engine drift")
    module_spec = importlib.util.spec_from_file_location("retained_mercator_audit", engine_file)
    engine = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(engine)
    values = {}
    for rank in sorted(ranks):
        if rank == 0:
            continue
        argument = Fraction(73, rank)
        check(argument >= 1, "Mercator logarithm input domain")
        reduced = argument
        while reduced >= 2:
            reduced /= 2
        if reduced >= Fraction(3, 2):
            reduced /= Fraction(3, 2)
        # These bounds also ensure the internal alternating series domain.
        check(1 <= reduced < Fraction(3, 2), "Mercator reduced domain")
        log_lower, log_upper = engine.logarithm(argument)
        exp_lower, exp_upper = ENDPOINT * log_lower, ENDPOINT * log_upper
        check(0 <= exp_lower <= exp_upper < Fraction(1, 10), "exponential domain")
        lo, hi = engine.exponential(exp_lower, exp_upper)
        check(lo <= hi, "ordered exponential enclosure")
        values[rank] = rank * lo, rank * hi
    return values


def affine(coefficients, values):
    """Enclose a linear expression directly, retaining signed coefficients."""
    lower = upper = Fraction(0)
    for rank, coefficient in coefficients.items():
        endpoints = [coefficient * endpoint for endpoint in values[rank]]
        lower += min(endpoints)
        upper += max(endpoints)
    return lower, upper


def ticks(pair):
    low, high = [number * PRECISION for number in pair]
    return low.numerator // low.denominator, -((-high.numerator) // high.denominator)


def independently_bounded_edges(prices, phi):
    records = {}
    raw = {}
    for rank in sorted(set(prices) - {0, 1, 48}):
        credit = 48 * prices[rank] + 13 * rank
        check(credit % 25 == 0, "residual credit lattice")
        weight = credit // 25
        check((weight - 37 * rank) % 48 == 0, "rank-credit congruence")
        # delta_r = 48 phi(r) - 48 v(r)/925 phi(1)
        #           + (v(r)/925-r) phi(48).
        pair = affine({rank: Fraction(48), 1: Fraction(-48 * credit, 925),
                       48: Fraction(credit, 925) - rank}, phi)
        label = "rank_" + str(rank)
        low, high = ticks(pair)
        records[label] = dict(label=label, rank=rank, step=weight % 37,
                              lower=low, upper=high)
        raw[label] = pair
    multiplier = affine({1: Fraction(48, 925), 48: Fraction(-1, 925)}, phi)
    check(multiplier[0] > 0, "positive supporting multiplier")
    slack = affine({1: Fraction(57600, 925), 48: Fraction(-1200, 925)}, phi)
    low, high = ticks(slack)
    records["slack"] = dict(label="slack", rank=None, step=26, lower=low, upper=high)
    raw["slack"] = slack
    check(len(records) == 43 and all(pair[0] > 0 for pair in raw.values()),
          "all 43 edge costs strictly positive")
    check(all(raw["rank_2"][1] < pair[0] for label, pair in raw.items() if label != "rank_2"),
          "rank two is the unique smallest edge, including slack")
    return records, raw


def profile_check(replicas, histogram, prices):
    check(type(replicas) is int and replicas > 0, "positive integer replica count")
    check(all(type(rank) is int and rank in prices and type(count) is int and count >= 0
              for rank, count in histogram.items()), "integral attainable bin counts")
    check(sum(rank * count for rank, count in histogram.items()) == 14382 * replicas,
          "witness rank balance")
    signed_total = sum(prices[rank] * count for rank, count in histogram.items())
    check(signed_total >= -3892 * replicas, "witness signed-price inequality")
    excess = 48 * (signed_total + 3892 * replicas)
    check(excess % 1200 == 0, "witness slack lattice")
    return excess


def inspect_receipt(receipt, prices, phi, edges, raw):
    check(receipt["status"] == "PASS_T37_INTEGRALITY_AUDIT", "receipt status")
    check(receipt["base_commit"] == BASE and Fraction(receipt["endpoint"]) == ENDPOINT,
          "base and endpoint")
    check(receipt["tick_denominator"] == PRECISION and receipt["legal_bin_patterns"] == 1163,
          "scale and pattern count")
    check(receipt["mass_per_replica"] == 14382 and receipt["signed_price_per_replica"] == -3892,
          "fixed inventory coefficients")
    check(receipt["credit_divisor"] == 25 and receipt["slack_modulus"] == 1200, "lattice metadata")
    check(receipt["upper"] == {str(rank): price for rank, price in prices.items()}, "DP price table")
    actual_edges = receipt["edges"]
    check(len(actual_edges) == len(edges), "complete edge inventory")
    check(len({item["label"] for item in actual_edges}) == len(edges), "distinct edge labels")
    check({item["label"]: item for item in actual_edges} == edges, "independent edge enclosures")
    potential = receipt["potential_ticks"]
    check(len(potential) == 37 and all(type(value) is int for value in potential)
          and potential[0] == 0, "integer potential normalized at zero")
    inequalities = 0
    for start in range(37):
        for edge in edges.values():
            finish = (start + edge["step"]) % 37
            check(potential[finish] - potential[start] <= edge["lower"], "potential edge inequality")
            inequalities += 1
    check(inequalities == receipt["checked_edge_inequalities"] == 1591, "1591 inequalities")
    # Synchronous Bellman-Ford: at round j, paths contain at most j edges.
    distances = [0] + [None] * 36
    for _ in range(36):
        previous = distances
        distances = previous[:]
        for start, distance in enumerate(previous):
            if distance is None:
                continue
            for edge in edges.values():
                finish = (start + edge["step"]) % 37
                candidate = distance + edge["lower"]
                if distances[finish] is None or candidate < distances[finish]:
                    distances[finish] = candidate
    check(distances == potential, "independent Bellman-Ford distances")
    rows = receipt["residue_certificates"]
    check(len(rows) == 37 and {row["replica_residue"] for row in rows} == set(range(37)),
          "exactly one witness for every residue")
    for row in rows:
        residue = row["replica_residue"]
        replicas = row["first_positive_T"]
        check(replicas == (residue or 37), "first positive representative")
        histogram = {int(rank): count for rank, count in row["profile"].items()}
        slack = profile_check(replicas, histogram, prices)
        check(slack == row["slack"] == 0, "zero-slack reported witnesses")
        labels = row["path"]
        check(all(label in edges for label in labels), "known path edges")
        off_support = Counter(edges[label]["rank"] for label in labels if label != "slack")
        check(dict(off_support) == {rank: count for rank, count in histogram.items()
                                    if rank not in (0, 1, 48) and count}, "path support matches witness")
        check(slack == 1200 * labels.count("slack"), "path slack matches witness")
        check(sum(edges[label]["step"] for label in labels) % 37 == 6 * replicas % 37,
              "path reaches required residue")
        lower = row["gap_lower_ticks"]
        upper = row["witness_gap_upper_ticks"]
        check(lower == potential[6 * replicas % 37] == sum(edges[label]["lower"] for label in labels),
              "witness attains lower-weight shortest path")
        check(upper == sum(edges[label]["upper"] for label in labels) and 0 <= upper - lower <= 10,
              "witness upper ticks and interval width")
        check(residue == 0 or lower > 0, "strict gap outside zero replica residue")
        # Direct full phi-numerator difference, independently of path costs.
        coefficients = {rank: Fraction(48 * count) for rank, count in histogram.items() if rank}
        coefficients[1] = coefficients.get(1, Fraction(0)) - Fraction(288 * replicas, 37)
        coefficients[48] = coefficients.get(48, Fraction(0)) - 14382 * replicas + Fraction(6 * replicas, 37)
        direct_low, direct_high = affine(coefficients, phi)
        check(Fraction(lower, PRECISION) <= direct_low <= direct_high <= Fraction(upper, PRECISION),
              "direct witness moment excess enclosed by receipt")
        # Equality-block extension establishes all positive T in the residue.
        extended = histogram.copy()
        extended[1] = extended.get(1, 0) + 6
        extended[48] = extended.get(48, 0) + 11086
        check(profile_check(replicas + 37, extended, prices) == slack, "equality-block extension")
    uniform = receipt["uniform_gap"]
    check(uniform["exact_expression"] == "c(2)-26*c(1)/37", "uniform expression")
    check((uniform["lower_ticks"], uniform["upper_ticks"]) == ticks(raw["rank_2"]), "uniform ticks")
    check(uniform["full_moment_denominator_per_T"] == 48 * 73 * 896, "moment normalization")
    check(uniform["sharp_relaxed_profile"] == {"T": 29, "1": 4, "2": 1, "48": 8689},
          "sharp T29 witness metadata")
    check(profile_check(29, {1: 4, 2: 1, 48: 8689}, prices) == 0, "sharp T29 premises")
    check(925 * 4 + 650 - 150 * 29 == 0, "sharp excess is exactly delta_2")
    return inequalities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "EXPECTED.json")
    arguments = parser.parse_args()
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    receipt = json.loads(arguments.receipt.read_text(encoding="utf-8"))
    check(manifest["base_commit"] == BASE, "manifest base")
    check(receipt["source_sha256"] == manifest["sha256"], "receipt source inventory")
    for relative, digest in manifest["sha256"].items():
        check(hashlib.sha256((REPOSITORY / relative).read_bytes()).hexdigest() == digest,
              "source drift: " + relative)
    prices = bin_dynamic_program()
    check(sum(capacity * count for capacity, count, _ in BIN_TYPES)
          - 9 * sum(width * count for (width, _), count in zip(HELPERS, (80, 32, 54, 122, 216))) == 14382,
          "independently derived inventory rank")
    check(sum(count * bonus for _, count, bonus in BIN_TYPES)
          + 9 * sum(price * count for (_, price), count in zip(HELPERS, (80, 32, 54, 122, 216))) == -3892,
          "independently derived signed inventory")
    check(48 * (-3892) + 13 * 14382 == 150 and Fraction(150, 925) == Fraction(6, 37),
          "credit demand and equality ratio")
    phi = read_phi(prices)
    edges, raw = independently_bounded_edges(prices, phi)
    checked = inspect_receipt(receipt, prices, phi, edges, raw)
    mutations = []
    for label in ("slack", "rank_44"):
        changed = deepcopy(receipt)
        changed["edges"] = [edge for edge in changed["edges"] if edge["label"] != label]
        mutations.append(("omit_" + label, changed))
    changed = deepcopy(receipt)
    changed["edges"][0]["lower"] += 1
    mutations.append(("overstate_edge", changed))
    changed = deepcopy(receipt)
    changed["potential_ticks"][28] += PRECISION * 100
    mutations.append(("inflate_potential", changed))
    changed = deepcopy(receipt)
    changed["residue_certificates"][1]["profile"]["48"] += 1
    mutations.append(("break_witness_mass", changed))
    changed = deepcopy(receipt)
    changed["residue_certificates"][1]["witness_gap_upper_ticks"] -= 1
    mutations.append(("understate_witness_upper", changed))
    changed = deepcopy(receipt)
    changed["residue_certificates"][1] = changed["residue_certificates"][0]
    mutations.append(("omit_replica_residue", changed))
    rejected = 0
    for name, changed in mutations:
        try:
            inspect_receipt(changed, prices, phi, edges, raw)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("independent negative control accepted: " + name)
    fractional = {1: Fraction(6, 37), 48: Fraction(11086, 37)}
    check(sum(rank * count for rank, count in fractional.items()) == 14382
          and sum(prices[rank] * count for rank, count in fractional.items()) == -3892,
          "fractional control satisfies both equalities")
    for replicas, histogram in ((1, fractional), (8, {48: 2397}), (1, {1: 1, 48: 299})):
        try:
            profile_check(replicas, histogram, prices)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("independent premise-removal control accepted")
    check(rejected == 10, "all independent negative controls rejected")
    print("PASS_T37_INDEPENDENT_CHECK: Mercator; DP 1163 patterns; "
          + str(checked) + " inequalities; Bellman-Ford 37 states; 37 direct moment witnesses; "
          + str(rejected) + " negative controls; sharp T29; no new kappa")


if __name__ == "__main__":
    main()
