#!/usr/bin/env python3
"""Independent rational bounds on the two frozen banked invoices."""

from argparse import ArgumentParser
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path


INVOICE = "a9aecf52d99d5370506b9dc6d03799241bebd2c03bbdcfa2dd5f45ec03c9d70d"
OUTER = "8e29f3ebb19c849884cfb87ef39431616774acfe95fa28a3cfe2e124abc6d202"
PEER = "00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38"
RESULT = "b1af8b101a40f25eea55a8b58443794a7db708389ad66c20adefbace12828e09"
PLAN = "509c44b078561a8868b68dab9f50b0b7d87d0976361d927bc8cc6bfdf1239393"
F = Fraction
Q = 1 << 160
BIT = F("0.00376669")
PEER_CLAIM = F("0.0037260455556")
CHILD_CLAIM = F("0.0037261023899")
PEER_BRACKET = tuple(map(F, ("0.00372604555571", "0.00372604555572")))
CHILD_BRACKET = tuple(map(F, ("0.0037261023900", "0.0037261023901")))


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def load_exact(path, expected):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected, f"frozen bytes changed: {path.name}")
    return json.loads(raw)


def outward(lower, upper):
    return F(lower * Q // 1, Q), F(-((-upper * Q) // 1), Q)


def log_unit(value):
    """Lower partial sum and upper geometric tail on log(value), 1 <= value <= 2."""
    u = (value - 1) / (value + 1)
    require(0 <= u <= F(1, 3), "range reduction for the logarithm")
    square, term, total = u * u, u, F()
    for index in range(28):
        total += 2 * term / (2 * index + 1)
        term *= square
    return total, total + 2 * term / (57 * (1 - square))


@lru_cache(maxsize=None)
def log_rank(rank):
    power = rank.bit_length() - 1
    low2, high2 = log_unit(F(2))
    low, high = log_unit(F(rank, 1 << power))
    return outward(power * low2 + low, power * high2 + high)


def positive_exp(value):
    """Bound exp(value) from its first 27 positive terms and the remaining tail."""
    require(0 <= value <= 1, "range reduction for the exponential")
    term, total = F(1), F(1)
    for index in range(1, 27):
        term *= value / index
        total += term
    first_omitted = term * value / 27
    return total, total + first_omitted / (1 - value / 28)


@lru_cache(maxsize=None)
def power_rank(rank, k_low, k_high):
    require(0 <= k_low <= k_high < 1, "positive exponent interval")
    log_low, log_high = log_rank(rank)
    x_low, x_high = outward((1-k_high) * log_low / 8, (1-k_low) * log_high / 8)
    low = positive_exp(x_low)[0]
    high = positive_exp(x_high)[1]
    low, high = outward(low, high)
    for _ in range(3):
        low, high = outward(low * low, high * high)
    return low, high


def moment(coefficients, k_low, k_high, derivative=False):
    low, high = F(), F()
    for rank, coeff in sorted(coefficients.items()):
        term_low, term_high = power_rank(rank, k_low, k_high)
        if derivative:
            log_low, log_high = log_rank(rank)
            term_low, term_high = -term_high * log_high, -term_low * log_low
        lower, upper = sorted((term_low * coeff, term_high * coeff))
        low, high = low + lower, high + upper
    return low, high


def read_history(invoice):
    p = {int(k): v for k, v in invoice["paid"].items()}
    t = {int(k): v for k, v in invoice["targets"].items()}
    require(all(1 <= k <= 137 and type(v) is int and v > 0
                for series in (p, t) for k, v in series.items()), "literal positive rank bill")
    require(sum(p.values()) == 101824 and sum(t.values()) == 21152, "full bill denominators")
    coeff = {k: t.get(k, 0) - p.get(k, 0) for k in p.keys() | t.keys()}
    require(sum(k * v for k, v in coeff.items()) == 1328, "retained signed rank surplus")
    return p, t, coeff


def per_side(invoice, received, claim, bracket, comparator, comparator_sign):
    _, _, coeff = read_history(invoice)
    require(F(received["decimal_claim"]) == claim and tuple(map(F, received["bracket"])) == bracket,
            "same directed endpoints shown in the application receipt")
    query = {claim: 1, claim + F(7, 10**14): 1, bracket[0]: 1, bracket[1]: -1}
    require(comparator not in query or query[comparator] == comparator_sign, "consistent comparator sign")
    query[comparator] = comparator_sign
    points = {}
    for point, sign in query.items():
        bounds = moment(coeff, point, point)
        require(bounds[0] > 0 if sign > 0 else bounds[1] < 0, f"strict moment sign at {point}")
        points[str(point)] = list(map(str, bounds))
    derivative = moment(coeff, PEER_CLAIM, BIT, derivative=True)
    require(derivative[1] < 0, "strictly decreasing moment on the shared comparison interval")
    return {
        "claim": str(claim), "bracket": list(map(str, bracket)), "target_minus_paid": points,
        "derivative_range": list(map(str, derivative)),
        "derivative_interval_kappa": [str(PEER_CLAIM), str(BIT)],
    }


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("invoices", "outer", "application", "peer-result", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--plan-sha256", required=True)
    args = parser.parse_args()
    require(args.plan_sha256 == PLAN, "registered independent rational price check")
    invoices = load_exact(args.invoices, INVOICE)
    outer = load_exact(args.outer, OUTER)
    published = load_exact(args.peer_result, PEER)["application"]
    applied = load_exact(args.application, RESULT)
    require(applied["status"] == "PASS_BANK24_ACTUAL16_APPLICATION_COMPONENT"
            and invoices["peer"] == published["invoice"], "same complete #7674 comparator")
    require(applied["graphs"]["peer"][0] == "d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098"
            and applied["graphs"]["candidate"][0] == "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150",
            "actual frozen peer and child graph identities")
    peer_p, peer_t, _ = read_history(invoices["peer"])
    child_p, child_t, child_coeff = read_history(invoices["candidate"])
    delta = {k: child_p.get(k, 0) - peer_p.get(k, 0) for k in peer_p.keys() | child_p.keys()}
    require({k: change for k, change in delta.items() if change} == {2: 16, 3: -32, 4: 16}
            and peer_t == child_t, "the only signed fee change is the paid rank redistribution")
    compared = PEER_BRACKET[1]
    improvement = moment({2: -16, 3: 32, 4: -16}, compared, compared)
    require(0 < improvement[0] <= improvement[1] < 1, "strict improvement with no rank-one fee")
    child_plus_fee = dict(child_coeff)
    child_plus_fee[1] -= 1
    control = moment(child_plus_fee, compared, compared)
    require(control[1] < 0, "a single added rank-one charge rejects the claimed comparison")
    gap = CHILD_CLAIM - compared
    require(gap == F(applied["strict_gap"]) == F(2841709, 50000000000000), "exact strict gap")
    result = {
        "status": "PASS_BANK24_REVIEW_INDEPENDENT_DIRECTED_PRICE",
        "scope": "Independent signed-rank moment brackets, derivative and added-price control",
        "inputs": {"invoices": INVOICE, "outer_receipt": OUTER, "application": RESULT,
                   "published_peer": PEER, "plan_receipt": PLAN,
                   "source": sha256(Path(__file__).read_bytes()).hexdigest()},
        "graphs": applied["graphs"], "caller_sha256": applied["caller_sha256"],
        "paid_count_each": 101824, "target_count_each": 21152,
        "rank_mass_surplus_each": 1328, "paid_delta": {2: 16, 3: -32, 4: 16},
        "target_delta": {}, "strict_gap": str(gap),
        "peer": per_side(invoices["peer"], outer["peer"], PEER_CLAIM, PEER_BRACKET, compared, -1),
        "candidate": per_side(invoices["candidate"], outer["candidate"], CHILD_CLAIM,
                              CHILD_BRACKET, compared, 1),
        "target_minus_paid_improvement_at_peer_upper": list(map(str, improvement)),
        "actual_child_added_one_rank_one_fee_control": list(map(str, control)),
    }
    for path, digest in ((args.invoices, INVOICE), (args.outer, OUTER),
                         (args.application, RESULT), (args.peer_result, PEER)):
        require(sha256(path.read_bytes()).hexdigest() == digest, f"input changed: {path.name}")
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(result["status"])


if __name__ == "__main__":
    main()
