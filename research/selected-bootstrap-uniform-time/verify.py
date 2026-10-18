#!/usr/bin/env python3
"""Exact corroboration of the conditional uniform-time lemma, not supplier replay.

Adam Gall, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import io
import json
from math import comb, factorial, isqrt
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
BIT = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil(value):
    value = Q(value)
    return -(-value.numerator // value.denominator)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def authenticate(payloads, sources):
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    require(set(payloads) == {row["path"] for row in rows}, "input inventory")
    for row in rows:
        require(digest(payloads[row["path"]]) == row["sha256"],
                "source hash: " + row["path"])
    for member in sources["archive_members"]:
        with tarfile.open(fileobj=io.BytesIO(payloads[member["path"]]), mode="r:gz") as archive:
            entry = archive.getmember(member["member"])
            require(entry.isfile(), "archive member must be a regular file")
            stream = archive.extractfile(entry)
            require(stream is not None, "archive member unavailable")
            with stream:
                data = stream.read()
        require(digest(data) == member["sha256"], "archive member hash")
    return len(rows)


def selected_stage(record, assembly, bit):
    require(record["certificate"] == ASSEMBLY, "selected certificate path")
    require(record["kappa"] == assembly["kappa"], "selected kappa binding")
    require(assembly["bit_supplier"]["path"] == BIT, "selected BIT source")
    require(assembly["bit_supplier"]["git_blob_sha1"] ==
            "e293ddc557742637f9f679f083a1a282d87b1b13", "selected BIT blob")
    require(assembly["surcharge_model"]["bit"] is True, "BIT surcharge required")
    nine = bit["nine"]
    b = Q(nine["bit_lower"])
    require(b == Q(assembly["bit_lower"]), "selected BIT saving")
    h = {int(r): count for r, count in nine["profile"].items()}
    require(all(type(v) is int and v > 0 for v in h.values()), "positive child counts")
    m, width = 64, nine["bit"]["live"]
    require(width == 28416 and max(h) == nine["bit"]["maxchild"] == 42,
            "selected producer dimensions")
    require(sum(r * count for r, count in h.items()) == nine["bit"]["rank_mass"],
            "selected profile mass")
    moment = [row for row in assembly["moments"]
              if row["side"] == "bit" and row["accept"] is True]
    require(len(moment) == 1, "one inherited accepting BIT moment")
    moment = moment[0]
    require(moment["surcharge"] is True and Q(moment["endpoint"]) == b,
            "inherited moment model")
    for engine in ("mercator", "base_two"):
        low, high = map(Q, moment[engine])
        require(-1 < low <= high < 0, "inherited moment upper endpoint")
    s = min(b, (1 - Q(1, 10**24)) * Q(assembly["complex_lower"])) - Q(1, 10**27)
    a = Q(384599, 10**10)
    require(0 <= a < s < b < 1, "stage exponent domain")
    aprime = (1 - s) * s + s * a
    require(aprime == Q(assembly["bootstrap"][0]["exponent"]), "first-stage exponent")
    coefficients = {r: Q(count, width) for r, count in h.items()}
    surcharge = Q(32 * m * m * sum(h.values()), 10**16 * width)
    coefficients[1] += surcharge
    mu1 = sum(value * Q(r, m) for r, value in coefficients.items())
    g1 = 1 - mu1
    rho = Q(max(coefficients), m)
    gt = (1 - rho) * (b - s)
    require(0 < g1 < 1 and 0 < gt < 1, "positive rational gaps")
    require(4 / g1 + 8 < 717 and 8 / gt < 401501, "uniform time coefficient")
    return {
        "m": m, "W": width, "maxchild": max(coefficients),
        "a": str(a), "s": str(s), "a_prime": str(aprime),
        "bit_lower": str(b), "rank_one_surcharge": str(surcharge),
        "linear_gap": str(g1), "stopped_gap_lower": str(gt),
        "linear_coefficient_strict_upper": 717,
        "stopped_coefficient_strict_upper": 401501,
        "K_if_each_primitive_coefficient_at_most_C": "C*max(401501,2*sigma)",
        "descriptor_degree_for_d1_b0": ceil(1 / s),
        "moment_certificate": "Inherited authenticated acceptance; no root recomputation",
    }


def constants(g1, gt, cadapt, cpeel, cleaf, cshift, cpad, crem, chi, sigma):
    require(g1 > 0 and gt > 0, "strict moment gaps")
    require(all(x >= 0 for x in (cadapt, cpeel, cleaf, cshift, cpad, crem, chi, sigma)),
            "nonnegative costs and stock coefficient")
    A, B = cadapt / g1, max(cleaf, cpeel / gt)
    K = max(4 * A + 6 * cshift + cpad + chi, 8 * B, 2 * sigma * chi, crem)
    return A, B, K


def sqrt_leq(coefficient, radicand, bound):
    """Check coefficient*sqrt(radicand) <= bound, with exact sign handling."""
    require(coefficient >= 0 and radicand >= 0, "square comparison domain")
    return bound >= 0 and coefficient * coefficient * radicand <= bound * bound


def table_cost(m, children, nmax, w, cadapt, cpeel, cleaf):
    values = [Q(0)]
    for n in range(1, nmax + 1):
        if n < m:
            values.append(cleaf * w)
        else:
            values.append(sum(c * values[r * (n // m)] for r, c in children.items())
                          + cadapt * n + cpeel * w)
    return values


def tree_cost(m, children, n, w, cadapt, cpeel, cleaf):
    """Independent explicit tree sum: no dynamic-programming cache or bound."""
    pending = [(Q(1), n)]
    total = Q(0)
    while pending:
        weight, width = pending.pop()
        if width == 0:
            continue
        if width < m:
            total += weight * cleaf * w
        else:
            total += weight * (cadapt * width + cpeel * w)
            quotient, _ = divmod(width, m)
            pending.extend((weight * c, r * quotient) for r, c in children.items())
    return total


def admit_node(actual, n, w, A, B):
    remainder = actual - A * n
    require(remainder <= 0 or remainder**2 <= B * B * w * w * n,
            "uniform induction bound")


def admit_wrapper(n, w, k, A, B, cshift, cpad, crem, chi, rhs):
    base = (4 * A + 6 * cshift) * n + cpad + crem * w + chi * k
    require(sqrt_leq(4 * B * w, n, rhs - base), "complete H2 bill")


def recursion_cases():
    # s=1/2, a=0. Perfect-square ratios make both moments rational.
    families = [(4, {1: Q(1, 2)}), (9, {1: Q(1, 2), 4: Q(1, 2)}),
                (16, {1: Q(1, 2), 4: Q(1)})]
    checked = 0
    for m, children in families:
        mu1 = sum(c * Q(r, m) for r, c in children.items())
        mutau = sum(c * Q(isqrt(r), isqrt(m)) for r, c in children.items())
        require(isqrt(m)**2 == m and all(isqrt(r)**2 == r for r in children),
                "rational square-root fixture")
        A, B, _ = constants(1 - mu1, 1 - mutau, Q(2), Q(3), Q(5),
                            Q(0), Q(0), Q(0), Q(0), Q(0))
        for w in (1, 2, 7, 31):
            values = table_cost(m, children, 512, w, Q(2), Q(3), Q(5))
            for n, actual in enumerate(values):
                require(actual == tree_cost(m, children, n, w, Q(2), Q(3), Q(5)),
                        "tree and dynamic recurrence disagree")
                admit_node(actual, n, w, A, B)
                checked += 1
    return checked


def wrapper_cases():
    g1, gt = Q(23, 32), Q(3, 8)  # m=16 family in recursion_cases.
    cadapt, cpeel, cleaf = Q(2), Q(3), Q(5)
    cshift, cpad, crem, chi = Q(7), Q(11), Q(13), Q(17)
    checked = 0
    for sigma in (Q(1, 100), Q(1, 2), Q(1), Q(3), Q(10)):
        A, B, K = constants(g1, gt, cadapt, cpeel, cleaf, cshift, cpad, crem, chi, sigma)
        for j in range(5):
            e, w, ep = 16**j, 4**j, 8**j  # e^s, e^(1-a') for s=1/2,a=0.
            top = min((e - 1) // 2, ceil(sigma * w * (1 + 4 * j)))
            ks = range(top + 1) if e <= 256 else sorted({0, min(1, top), top // 2, top})
            for k in ks:
                n = (e - k) // w
                rhs = K * (w + ep + w * (1 + 4 * j) + w)
                admit_wrapper(n, w, k, A, B, cshift, cpad, crem, chi, rhs)
                require(n * w <= e - k < (n + 1) * w, "residual width")
                checked += 1
    # Empty body can occur at small widths: s=3/4,e=9,w=6,k=4.
    require(5**4 < 9**3 <= 6**4 and 2 * 4 < 9 and (9 - 4) // 6 == 0,
            "empty atom-body boundary")
    require(tree_cost(16, {1: Q(1)}, 0, 6, Q(2), Q(3), Q(5)) == 0,
            "empty body costs no recursive call")
    return checked


def descriptor_cases():
    checked = 0
    for degree in range(13):
        cap = 2**degree * factorial(degree)
        partial = Q(0)
        for w in range(1, 129):
            term = comb(w + degree - 1, degree)
            require(w**degree <= factorial(degree) * term, "rising factorial inequality")
            partial += Q(term, 2**w)
            require(partial < 2**degree, "positive series partial sum")
            require(Q(w**degree, 2**w) <= cap, "all-width descriptor cap")
            checked += 1
    return checked


def ordinary_body(head, data, row, restore=True):
    """Literal five-operation wrapper on two radix-3 atoms; arbitrary row."""
    h, d = divmod(head, 3), divmod(data, 3)
    d = tuple((y - x) % 3 for x, y in zip(h, d))
    # A completed reversed call may temporarily leave the genuine row range.
    row = (row + 1) % 4
    h, d = d[::-1], h[::-1]
    row = (row - 1) % 4
    d = tuple((y + x) % 3 for x, y in zip(h, d))
    row = (row + 1) % 4
    h, d = d[::-1], h[::-1]
    if restore:
        row = (row - 1) % 4
    d = tuple((x - y) % 3 for x, y in zip(h, d))
    return 3 * h[0] + h[1], 3 * d[0] + d[1], row


def endpoint_cases():
    # q=3,k=1, body range 9, two spectator values, row divisor 2.
    # Genuine preceding row range 3 pads to 4, a nondivisible case.
    checked = 0
    for hhi in range(3):
        for dh in range(3):
            for hb in range(9):
                for db in range(9):
                    for spectator in range(2):
                        left, right, row = ordinary_body(hb, db, hhi)
                        z, other = spectator, dh
                        require(row < 3, "genuine padded range invariant")
                        completed = (other, left, z, row, right)
                        require(completed == (dh, db, spectator, hhi, hb),
                                "completed high/body interchange")
                        checked += 1
    return checked


def rejection(action, expected):
    try:
        action()
    except ValueError as exc:
        require(expected in str(exc), "wrong rejection: " + str(exc))
        return
    raise ValueError("control was accepted: " + expected)


def controls(record, assembly, bit, payloads, sources):
    rejected = []

    def check(name, action, expected):
        rejection(action, expected)
        rejected.append(name)

    zero = Q(0)
    check("non_strict_moment", lambda: constants(zero, Q(1), *([Q(1)] * 8)),
          "strict moment gaps")
    check("negative_cost", lambda: constants(Q(1), Q(1), Q(-1), *([Q(1)] * 7)),
          "nonnegative costs")
    # Build the independent actual costs, then delete the charged coefficient.
    leaf = tree_cost(16, {}, 1, 1, zero, zero, Q(10))
    check("omitted_leaf_charge", lambda: admit_node(leaf, 1, 1, zero, zero),
          "uniform induction bound")
    node = tree_cost(16, {}, 16, 1, Q(1), zero, zero)
    check("omitted_node_charge", lambda: admit_node(node, 16, 1, zero, zero),
          "uniform induction bound")
    # q^k=3, divisor=2: compare two calls on the actual padded logical volume.
    exact_padding = Q(ceil(Q(3, 2)) * 2, 3)
    check("omitted_padding_multiplier",
          lambda: require(2 * exact_padding <= 2, "padded body bill"), "padded body bill")
    # Actual Chi=1; a proposed bound obtained by deleting Chi pays nothing.
    _, _, missing_high_K = constants(Q(1), Q(1), *([zero] * 7), Q(1))
    check("omitted_high_exchange",
          lambda: admit_wrapper(9, 16, 100, zero, zero, zero, zero, zero, Q(1),
                                missing_high_K * (16 + 64 + 144 + 16)),
          "complete H2 bill")
    # Mutate the literal wrapper's second row restoration, not the expected tuple.
    check("unrestored_row",
          lambda: require(ordinary_body(1, 5, 2, restore=False)[2] < 3,
                          "genuine row restriction"), "genuine row restriction")
    cap = 2**3 * factorial(3)
    check("incomplete_fiber", lambda: require(100**3 <= cap, "fiber normalization"),
          "fiber normalization")
    # Cost equals w except for w=7, so its eventual coefficient is one.
    spike = lambda w: 1000 if w == 7 else w
    require(all(spike(w) == w for w in range(8, 32)), "eventual spike fixture")
    check("eventual_not_uniform_leaf",
          lambda: admit_node(Q(spike(7)), 1, 7, zero, Q(1)), "uniform induction bound")
    bad = deepcopy(assembly)
    bad["surcharge_model"]["bit"] = False
    check("missing_selected_surcharge", lambda: selected_stage(record, bad, bit), "BIT surcharge")
    bad2 = deepcopy(assembly)
    for row in bad2["moments"]:
        if row["side"] == "bit" and row["accept"]:
            row["base_two"][1] = "0"
    check("non_strict_inherited_receipt", lambda: selected_stage(record, bad2, bit),
          "inherited moment upper")
    bad3 = deepcopy(bit)
    bad3["nine"]["profile"]["1"] += 1
    check("changed_selected_profile", lambda: selected_stage(record, assembly, bad3),
          "selected profile mass")
    bad4 = deepcopy(assembly)
    bad4["bootstrap"][0]["exponent"] = "0"
    check("detached_stage_exponent", lambda: selected_stage(record, bad4, bit),
          "first-stage exponent")
    corrupt = dict(payloads)
    corrupt[BIT] += b" "
    check("source_byte_drift", lambda: authenticate(corrupt, sources), "source hash")
    bad_sources = deepcopy(sources)
    bad_sources["archive_members"][0]["sha256"] = "0" * 64
    check("archive_member_drift", lambda: authenticate(payloads, bad_sources), "archive member hash")
    require(not sqrt_leq(Q(1), 1, Q(-1)), "square sign guard")
    rejected.append("negative_square_bound")
    return rejected


def compare_receipt(expected, actual):
    require(expected == actual, "canonical receipt mismatch")


def evaluate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    payloads = {row["path"]: (ROOT / row["path"]).read_bytes()
                for row in sources["files"] if row["usage"] == "input"}
    source_count = authenticate(payloads, sources)
    record = json.loads(payloads["certificates/selected-result.json"])
    require(record["certificate_sha256"] == digest(payloads[ASSEMBLY]), "selected receipt hash")
    assembly, bit = json.loads(payloads[ASSEMBLY]), json.loads(payloads[BIT])
    stage = selected_stage(record, assembly, bit)
    result = {
        "status": "PASS_SELECTED_BOOTSTRAP_UNIFORM_TIME",
        "scope": "Conditional uniform lifting lemma; native selected stage1; no stock coefficient or supplier adoption",
        "source_files_authenticated": source_count,
        "archive_members_authenticated": len(sources["archive_members"]),
        "selected_stage": stage,
        "recursion_tree_and_induction_cases": recursion_cases(),
        "complete_wrapper_bill_cases": wrapper_cases(),
        "descriptor_inequality_cases": descriptor_cases(),
        "padded_complete_endpoint_cases": endpoint_cases(),
        "controls_rejected": controls(record, assembly, bit, payloads, sources),
        "remaining_premises": ["uniform primitive/compiler and normalized logical-volume contracts",
                               "actual same-domain stock envelope sigma", "inherited exact endpoint and tape contracts"],
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write once to a new output path")
    args = parser.parse_args()
    result = evaluate()
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        compare_receipt(json.loads((PACKAGE / "RESULT.json").read_text()), result)
    print(result["status"], "stage=1", "K=C*max(401501,2*sigma)",
          "recurrence_cases=" + str(result["recursion_tree_and_induction_cases"]),
          "wrapper_cases=" + str(result["complete_wrapper_bill_cases"]),
          "controls_rejected=" + str(len(result["controls_rejected"])))


if __name__ == "__main__":
    main()
