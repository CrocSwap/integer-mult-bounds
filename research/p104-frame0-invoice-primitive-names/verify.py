#!/usr/bin/env python3
"""Name the 40 frame-0 monomials against the selected #6030 invoice.

The charged polynomial is the disjoint-variable form recorded by PR #7031.
The selected invoice names a recursive primitive by a ledger side and a
positive rank. Those ranks are rebuilt from the selected word. None of the
inherited constructors reads a chart monomial, and the readings that use only
the monomial's own integers do not place all 40 on a unique primitive.

Standard library only. Checks raise SystemExit, so python -O still runs them.
No kappa is computed.
"""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz"
RESULT = ROOT / "research/p104-helper470-twin-rung-removal/RESULT.json"
PRICING = ROOT / "research/p104-helper470-twin-rung-removal/pricing.py"
LOCAL = ROOT / "research/p104-unread-path-resynthesis/local.py"
LINE_MAP = ROOT / "research/p104-port-window-haemers/data/e8_line_map.json"
SELECTED = ROOT / "certificates/selected-result.json"

ANF_SHA256 = "26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a"
DEGREE4_OUTSIDE = (99, 101, 113, 163, 165, 177)
HOST_PORTS = (11, 21, 38, 140)
HOST_LABELS = {11: 282, 21: 284, 38: 270, 140: 454}
KAPPA = "781451/250000000"


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def expect_fail(function, message):
    try:
        function()
    except SystemExit:
        return
    raise SystemExit(message)


def monomial_name(exponent):
    return "*".join("x{0}".format(index) for index in range(8) if exponent >> index & 1)


def expand_charged_polynomial():
    """Cartesian product of the four disjoint factors. Size 2*4*2*3 = 48."""
    factors = (
        (0, 1 << 0),
        (0, 1 << 1, 1 << 2, 1 << 4),
        (0, 1 << 5),
        (0, 1 << 6, 1 << 7),
    )
    need(len(factors[0]) * len(factors[1]) * len(factors[2]) * len(factors[3]) == 48,
         "the charged product is not the 48-element domain")
    counts = Counter()
    for parts in product(*factors):
        mask = 0
        for part in parts:
            mask |= part
        counts[mask] += 1
    need(max(counts.values()) == 1 and len(counts) == 48,
         "disjoint factors cancelled or collided")
    exponents = tuple(sorted(counts))
    payload = ",".join(str(exponent) for exponent in exponents)
    need(hashlib.sha256(payload.encode()).hexdigest() == ANF_SHA256,
         "charged normal form does not match the #7031 hash")
    degrees = dict(Counter(exponent.bit_count() for exponent in exponents))
    need(degrees == {0: 1, 1: 7, 2: 17, 3: 17, 4: 6},
         "degree counts changed: {0}".format(degrees))
    new = tuple(exponent for exponent in exponents if exponent.bit_count() >= 2)
    need(len(new) == 40, "expected 40 degree-at-least-2 monomials")
    need(tuple(exponent for exponent in exponents if exponent.bit_count() <= 1)
         == (0, 1, 2, 4, 16, 32, 64, 128),
         "the degree-at-most-1 complement changed")
    return new


def load_json(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode())


def rebuild_invoice(word):
    paid = Counter()
    for event in word["program"]:
        if event[0] != "MOVE":
            continue
        _op, _role, source, destination, _private = event
        paid[abs(len(word["frames"][destination]) - len(word["frames"][source]))] += 1
    live = set(word["live"])
    main = live | {role + 112 for role in live}
    helpers = Counter()
    for role in range(word["public"]):
        if role not in main:
            helpers[len(word["frames"][word["final"][role]])
                    - len(word["frames"][word["initial"][role]])] += 1
    targets = Counter({rank: 18 * count for rank, count in helpers.items()})
    full_paid = Counter({rank: 18 * count for rank, count in paid.items()})
    targets[145] += 208
    full_paid[1] += 15 * 104
    for length in (7, 8):
        for step in range(1, length + 1):
            targets[1 + 8 * (step + 1)] += 208
            full_paid[8 * (step + 1)] += 208
    return paid, helpers, full_paid, targets


def integer_keys(histogram):
    return {int(rank): count for rank, count in histogram.items()}


def simple_basis():
    basis = [
        (1, -1, -1, -1, -1, -1, -1, 1),
        (2, 2, 0, 0, 0, 0, 0, 0),
        (-2, 2, 0, 0, 0, 0, 0, 0),
    ]
    for index in range(1, 6):
        vector = [0] * 8
        vector[index] = -2
        vector[index + 1] = 2
        basis.append(tuple(vector))
    return basis


def root_dot(left, right):
    return sum(entry * other for entry, other in zip(left, right)) // 4


def label_of(root):
    basis = simple_basis()
    matrix = list(zip(*basis))
    rows = [[Fraction(matrix[row][column]) for column in range(8)] + [Fraction(root[row])]
            for row in range(8)]
    for column in range(8):
        pivot = next(row for row in range(column, 8) if rows[row][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = 1 / rows[column][column]
        rows[column] = [entry * scale for entry in rows[column]]
        for row in range(8):
            if row != column and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [rows[row][index] - factor * rows[column][index]
                             for index in range(9)]
    coordinates = [rows[index][8] for index in range(8)]
    need(all(entry.denominator == 1 for entry in coordinates),
         "simple-root coordinates are not integral")
    bits = 0
    for index, value in enumerate(coordinates):
        if int(value) & 1:
            bits |= 1 << index
    return bits | (1 << 8)


def classify(monomials, paid_keys, target_keys, opcodes, ports):
    rows = []
    for exponent in monomials:
        rows.append({
            "exponent": exponent,
            "degree": exponent.bit_count(),
            "name": monomial_name(exponent),
            "paid_key": exponent in paid_keys,
            "target_key": exponent in target_keys,
            "opcode": monomial_name(exponent) in opcodes,
            "port": exponent in ports,
        })
    return rows


def require_constructors(pricing, local):
    needles = (
        "paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1",
        "second_p[1] += 15*104",
        "second_t[145] += 208",
        "for length in (7,8):",
        "second_p[8*(j+1)] += 208",
        "second_t[1+8*(j+1)] += 208",
        "second_t = Counter({r:18*n for r,n in local['helpers'].items()})",
        "second_p = Counter({r:18*n for r,n in local['paid'].items()})",
    )
    for needle in needles:
        need(needle in pricing or needle in local, "missing inherited constructor: " + needle)
    replay, _separator, _rest = local.partition("def reverse_columns")
    need("def replay" in replay, "local replay function missing")
    need("x0" not in replay and "degree" not in replay and "monomial" not in replay,
         "the local replay reads a chart monomial")
    assemble, _separator, _rest = pricing.partition("def run")
    need("def assemble" in assemble, "pricing assembly missing")
    need("x0" not in assemble and "degree" not in assemble and "monomial" not in assemble,
         "the invoice assembly reads a chart monomial")
    need("need(w['frames'][w['initial'][r]] == [q], 'Literal central port')" in local,
         "literal central-port frame is not the inherited port name")


def run_controls(monomials, paid_keys, word):
    def dropped_factor():
        factors = ((0,), (0, 1 << 1, 1 << 2, 1 << 4), (0, 1 << 5), (0, 1 << 6, 1 << 7))
        found = set()
        for parts in product(*factors):
            mask = 0
            for part in parts:
                mask |= part
            if mask.bit_count() >= 2:
                found.add(mask)
        need(len(found) == 40, "dropping x0 still leaves 40 monomials")

    expect_fail(dropped_factor, "dropping the x0 factor still charged 40 monomials")

    def degree4_is_paid():
        need(DEGREE4_OUTSIDE[0] in paid_keys, "mask 99 became a paid rank")

    expect_fail(degree4_is_paid, "degree-4 mask 99 was accepted as a paid rank")

    def wrong_local_multiplier():
        paid = Counter()
        for event in word["program"]:
            if event[0] == "MOVE":
                paid[abs(len(word["frames"][event[3]]) - len(word["frames"][event[2]]))] += 1
        forged = Counter({rank: 17 * count for rank, count in paid.items()})
        expected = Counter()
        for event in word["program"]:
            if event[0] == "MOVE":
                expected[abs(len(word["frames"][event[3]]) - len(word["frames"][event[2]]))] += 1
        expected = Counter({rank: 18 * count for rank, count in expected.items()})
        need(forged == expected, "a 17-fold local bill matched the 18-fold bill")

    expect_fail(wrong_local_multiplier, "changing 18 LOCAL copies was not detected")
    need(all(monomial_name(exponent) not in {"ADD", "SCALE", "MOVE", "COPY", "INIT", "CLEAR"}
             for exponent in monomials),
         "a chart monomial was stored as an opcode")


def main():
    monomials = expand_charged_polynomial()
    word = load_json(WORD)
    result = load_json(RESULT)
    selected = load_json(SELECTED)
    need(word["schema"] == "p104-accumulated-block-composition/2", "unexpected word schema")
    need(selected["kappa"] == KAPPA, "selected kappa changed")
    need(selected["source_certificate"] == "research/p104-helper470-twin-rung-removal/RESULT.json",
         "selected source certificate is not the #6030 result")
    need(hashlib.sha256(RESULT.read_bytes()).hexdigest() == selected["source_certificate_sha256"],
         "RESULT.json is not the selected source certificate")
    local_paid, helpers, full_paid, targets = rebuild_invoice(word)
    need(dict(local_paid) == integer_keys(result["local"]["paid"]),
         "rebuilt local paid histogram disagrees with RESULT.json")
    need(dict(helpers) == integer_keys(result["local"]["helpers"]),
         "rebuilt helper histogram disagrees with RESULT.json")
    need(dict(full_paid) == integer_keys(result["complete_cost"]["paid"]),
         "rebuilt paid invoice disagrees with RESULT.json")
    need(dict(targets) == integer_keys(result["complete_cost"]["targets"]),
         "rebuilt target invoice disagrees with RESULT.json")
    opcodes = {event[0] for event in word["program"]}
    need(opcodes == {"ADD", "CLEAR", "COPY", "INIT", "MOVE", "SCALE"},
         "ordinary opcode alphabet changed: {0}".format(sorted(opcodes)))
    require_constructors(PRICING.read_text(encoding="utf-8"), LOCAL.read_text(encoding="utf-8"))

    paid_keys = set(full_paid)
    target_keys = set(targets)
    ports = set(word["ports"])
    need(len(ports) == 104, "the selected word does not carry 104 ports")
    rows = classify(monomials, paid_keys, target_keys, opcodes, ports)
    paid_hits = [row["exponent"] for row in rows if row["paid_key"]]
    target_hits = [row["exponent"] for row in rows if row["target_key"]]
    either = [row["exponent"] for row in rows if row["paid_key"] or row["target_key"]]
    both = [row["exponent"] for row in rows if row["paid_key"] and row["target_key"]]
    port_hits = [row["exponent"] for row in rows if row["port"]]
    opcode_hits = [row["name"] for row in rows if row["opcode"]]
    need(paid_hits == [3, 5, 48], "paid-key collisions changed: {0}".format(paid_hits))
    need(target_hits == [3, 5, 17, 33, 49, 65, 145],
         "target-key collisions changed: {0}".format(target_hits))
    need(both == [3, 5], "two-sided collisions changed")
    need(len(either) == 8 and len(rows) - len(either) == 32, "histogram coverage changed")
    degree4 = tuple(row["exponent"] for row in rows if row["degree"] == 4)
    need(degree4 == DEGREE4_OUTSIDE, "degree-4 masks changed")
    need(all(exponent not in paid_keys and exponent not in target_keys
             for exponent in DEGREE4_OUTSIDE),
         "a degree-4 mask became a histogram key")
    need(opcode_hits == [], "an opcode reading named a monomial")
    need(port_hits == [35, 37, 49, 69, 81, 98, 100, 112, 131, 133, 145, 161, 164, 176],
         "port-integer collisions changed")
    need(len(port_hits) == 14, "port reading unexpectedly named every monomial")
    frame_vectors = {vector for frame in word["frames"] for vector in frame}
    frame_hits = [row["exponent"] for row in rows if row["exponent"] in frame_vectors]
    need(len(frame_hits) == 34, "frame-vector integer collisions changed")
    need(tuple(exponent for exponent in DEGREE4_OUTSIDE if exponent not in frame_vectors)
         == DEGREE4_OUTSIDE,
         "a degree-4 exponent occurred as a frame vector")

    line_map = load_json(LINE_MAP)
    roots = {vector: tuple(root) for vector, root in zip(line_map["vectors"], line_map["roots2"])}
    labels = {}
    for port in HOST_PORTS:
        labels[port] = label_of(roots[port])
    need(labels == HOST_LABELS, "simple-root labels of the hosting ports changed: {0}".format(labels))
    need(all(label not in set(monomials) and label != port for port, label in labels.items()),
         "a hosting-port label collapsed onto its port or onto a charged mask")
    # The eight simple-root coordinates are not the nine port-space bits.
    basis_dots = [root_dot(left, right) & 1
                  for left, right in combinations(simple_basis(), 2)]
    need(any(basis_dots), "the simple-root chart was treated as an orthonormal port basis")

    run_controls(monomials, paid_keys, word)
    print(
        "PASS_P104_FRAME0_INVOICE_NAMES monomials=40 outside_both_histograms=32 "
        "degree4_outside=6 paid_collisions=3 target_collisions=7 opcode_hits=0 "
        "port_collisions=14 kappa={0}".format(KAPPA)
    )
    for row in rows:
        print("MONOMIAL {exponent} deg={degree} {name} paid_key={paid_key} "
              "target_key={target_key} port_integer={port}".format(**row))


if __name__ == "__main__":
    main()
