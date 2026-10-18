#!/usr/bin/env python3
"""Exact, solver-free replay; standard library; checks survive python -O.

Prepared by Alexander Templeton with substantial OpenAI Codex assistance.
Apache-2.0. See PROOF.md for the all-width argument and pricing premise.
"""

import argparse
from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Rational rank via integer row operations and primitive row reduction."""
    a = [list(row) for row in rows]
    if not a:
        return 0
    require(len({len(row) for row in a}) == 1, "ragged matrix")
    r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(r + 1, len(a)):
            if a[i][col]:
                p, f = a[r][col], a[i][col]
                a[i] = [p * x - f * y for x, y in zip(a[i], a[r])]
                divisor = 0
                for value in a[i]:
                    divisor = gcd(divisor, value)
                if divisor:
                    a[i] = [value // divisor for value in a[i]]
        r += 1
        if r == len(a):
            break
    return r


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def left_basis(v):
    rows = [[], [], [], []]
    for start in (0, 4):
        a, b, c, d = v[start:start + 4]
        for row, block in zip(rows, ((a, b, c, d), (-b, a, -d, c),
                                     (-c, d, a, -b), (-d, -c, b, a))):
            row.extend(block)
    return tuple(tuple(row) for row in rows)


def e8_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for x, y in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = x, y
            roots.append(tuple(v))
    roots.extend(v for v in product((-1, 1), repeat=8) if v.count(-1) % 2 == 0)
    return sorted(roots)


def geometry(roots):
    require(len(roots) == len(set(roots)) == 240, "root cardinality")
    lines = {}
    for v in roots:
        require(len(v) == 8 and dot(v, v) == 8, "root norm")
        basis = left_basis(v)
        require([[dot(x, y) for y in basis] for x in basis] ==
                [[8 * (i == j) for j in range(4)] for i in range(4)],
                "quaternion basis Gram")
        # The basis has Gram 8I, so this is exactly eight times its projector.
        key = tuple(sum(row[i] * row[j] for row in basis)
                    for i in range(8) for j in range(8))
        lines.setdefault(key, []).append(v)
    require(len(lines) == 10, "line count")
    require({len(v) for v in lines.values()} == {24}, "line root counts")
    bases = [left_basis(min(lines[key])) for key in sorted(lines)]
    mates = []
    pairing_ranks = []
    for i, a in enumerate(bases):
        ranks = [rank([[dot(x, y) for y in b] for x in a]) for b in bases]
        require(ranks[i] == 4 and ranks.count(0) == 1 and ranks.count(4) == 9,
                "singleton pairing ranks")
        mates.append(ranks.index(0))
        pairing_ranks.append(ranks)
    pairs = [(i, j) for i, j in enumerate(mates) if i < j]
    check_pairs(10, pairs)
    for i, j in combinations(range(10), 2):
        require(rank(bases[i] + bases[j]) == 8, "two-line span")
    return pairs, {
        "root_count": 240,
        "line_count": 10,
        "roots_per_line": 24,
        "basis_rows": bases,
        "mate_pairs": pairs,
        "singleton_pairing_ranks": pairing_ranks,
        "two_line_spans_checked": 45,
    }


def check_pairs(n, pairs):
    require(n > 0 and n % 2 == 0, "positive even port count")
    require(sorted(t for pair in pairs for t in pair) == list(range(n)),
            "perfect matching")
    require(all(len(pair) == 2 and pair[0] != pair[1] for pair in pairs),
            "matching pair")


def transversals(pairs):
    return [sum(1 << t for t in choice) for choice in product(*pairs)]


def charge(readers, sources, pairs):
    if not readers or not sources:
        return 0
    if readers.bit_count() == sources.bit_count() == 1:
        if any({readers, sources} == {1 << i, 1 << j} for i, j in pairs):
            return 0
    return 1 if min(readers.bit_count(), sources.bit_count()) == 1 else 2


def local_certificate(n, pairs, ts=None, denominator=None):
    check_pairs(n, pairs)
    expected_ts = transversals(pairs)
    ts = expected_ts if ts is None else ts
    denominator = 1 << (n // 2 - 1) if denominator is None else denominator
    require(sorted(ts) == sorted(expected_ts), "transversal list")
    require(all(sum(bool(t & (1 << i)) for t in ts) == denominator
                for i in range(n)), "unit vertex coverage")
    hit = [sum(1 << i for i, t in enumerate(ts) if mask & t)
           for mask in range(1 << n)]
    counts = [0, 0, 0]
    maximum_hits = [0, 0, 0]
    for readers in range(1 << n):
        for sources in range(1 << n):
            c = charge(readers, sources, pairs)
            both = (hit[readers] & hit[sources]).bit_count()
            require(both <= denominator * c, "local weighted inequality")
            counts[c] += 1
            maximum_hits[c] = max(maximum_hits[c], both)
    return {"support_pairs": (1 << n) ** 2, "transversal_masks": ts,
            "weight": f"1/{denominator}", "charge_counts": counts,
            "maximum_hits_by_charge": maximum_hits}


@dataclass(frozen=True)
class Message:
    sources: int
    readers: int
    width: int
    outputs: tuple


@dataclass(frozen=True)
class Code:
    widths: tuple
    pairs: tuple
    messages: tuple


def states(widths):
    return list(product(*(range(1 << b) for b in widths)))


def selected(state, mask):
    return tuple(x for i, x in enumerate(state) if mask & (1 << i))


def single_valued(table, key, value, reason):
    require(key not in table or table[key] == value, reason)
    table[key] = value


def audit_code(code, extra_side_information=False):
    n = len(code.widths)
    check_pairs(n, code.pairs)
    require(all(type(b) is int and b >= 0 for b in code.widths), "input width")
    xs = states(code.widths)
    all_mask = (1 << n) - 1
    for msg in code.messages:
        require(type(msg.width) is int and msg.width >= 0, "message width")
        require(0 <= msg.sources <= all_mask and 0 <= msg.readers <= all_mask,
                "support domain")
        require(len(msg.outputs) == len(xs), "truth table size")
        observed = {}
        for x, y in zip(xs, msg.outputs):
            require(type(y) is int and 0 <= y < (1 << msg.width),
                    "message alphabet")
            single_valued(observed, selected(x, msg.sources), y,
                          "undeclared source dependency")
    mates = {a: b for a, b in code.pairs for a, b in ((a, b), (b, a))}
    for t in range(n):
        observed = {}
        for index, x in enumerate(xs):
            side = selected(x, all_mask ^ (1 << t)) if extra_side_information else (x[mates[t]],)
            view = side + tuple(msg.outputs[index] for msg in code.messages
                                if msg.readers & (1 << t))
            single_valued(observed, view, x[t], "decoder collision")
    cost = sum(msg.width * charge(msg.readers, msg.sources, code.pairs)
               for msg in code.messages)
    cut_states = 0
    if not extra_side_information:
        for t in transversals(code.pairs):
            observed = {}
            relevant = [msg for msg in code.messages if msg.readers & t and msg.sources & t]
            require(sum(code.widths[i] for i in range(n) if t & (1 << i)) <=
                    sum(msg.width for msg in relevant), "cut capacity")
            for index, x in enumerate(xs):
                key = selected(x, all_mask ^ t) + tuple(msg.outputs[index] for msg in relevant)
                single_valued(observed, key, selected(x, t), "transcript collision")
                cut_states += 1
        require(cost >= sum(code.widths), "copy floor")
    return {"widths": list(code.widths), "states": len(xs), "messages": len(code.messages),
            "cost": cost, "floor": sum(code.widths), "cut_states": cut_states}


def broadcast_code(n, width):
    pairs = tuple((i, n - 1 - i) for i in range(n // 2))
    xs = states((width,) * n)
    outputs = []
    for x in xs:
        z = sum((x[a] ^ x[b]) << (i * width) for i, (a, b) in enumerate(pairs))
        # Toffoli is its own inverse; the third bit changes by the first two's AND.
        z ^= ((z & 1) & ((z >> 1) & 1)) << 2
        outputs.append(z)
    mask = (1 << n) - 1
    return Code((width,) * n, pairs, (Message(mask, mask, n // 2 * width, tuple(outputs)),))


def nonlinear_witness(code):
    lookup = dict(zip(states(code.widths), code.messages[0].outputs))
    zero = (0,) * len(code.widths)
    units = []
    for i, b in enumerate(code.widths):
        for bit in range(b):
            x = [0] * len(code.widths)
            x[i] = 1 << bit
            units.append(tuple(x))
    for a, b in combinations(units, 2):
        ab = tuple(x ^ y for x, y in zip(a, b))
        if lookup[zero] ^ lookup[a] ^ lookup[b] ^ lookup[ab]:
            return {"a": a, "b": b, "nonzero_second_difference":
                    lookup[zero] ^ lookup[a] ^ lookup[b] ^ lookup[ab]}
    raise ValueError("expected genuinely nonlinear encoder")


def reject(name, action, expected):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected, f"{name}: wrong rejection: {error}")
        return name
    raise ValueError(f"negative control accepted: {name}")


def build_receipt():
    roots = e8_roots()
    pairs, geo = geometry(roots)
    local = local_certificate(10, pairs)
    binary = broadcast_code(10, 1)
    vector = broadcast_code(4, 2)
    # A mate-only transmission has zero charge and cannot help a transversal.
    vector_xs = states(vector.widths)
    vector = replace(vector, messages=vector.messages +
                     (Message(1 << 3, 1, 2, tuple(x[3] for x in vector_xs)),))
    widths = (0, 1, 2, 1)
    unequal = Code(widths, ((0, 3), (1, 2)), tuple(
        Message(1 << t, 1 << t, b, tuple(x[t] for x in states(widths)))
        for t, b in enumerate(widths)))
    examples = {}
    for name, code in (("nonlinear_ten_ports", binary), ("nonlinear_vector_with_free_mate", vector),
                       ("unequal_width_direct", unequal)):
        examples[name] = audit_code(code)
        require(examples[name]["cost"] == examples[name]["floor"], "attainment")
        if name != "unequal_width_direct":
            examples[name]["nonlinear_witness"] = nonlinear_witness(code)

    def changed(**kwargs):
        return replace(binary, messages=(replace(binary.messages[0], **kwargs),))

    controls = [
        reject("duplicate_root", lambda: geometry(roots[:-1] + roots[:1]), "root cardinality"),
        reject("wrong_root_norm", lambda: geometry([(1,) + (0,) * 7] + roots[1:]), "root norm"),
        reject("nonmatching_mates", lambda: local_certificate(10, pairs[:-1]), "perfect matching"),
        reject("omitted_transversal", lambda: local_certificate(10, pairs, transversals(pairs)[:-1]), "transversal list"),
        reject("wrong_weight", lambda: local_certificate(10, pairs, denominator=17), "unit vertex coverage"),
        reject("width_not_charged", lambda: audit_code(changed(width=1)), "message alphabet"),
        reject("negative_width", lambda: audit_code(changed(width=-1)), "message width"),
        reject("missing_source", lambda: audit_code(changed(sources=1022)), "undeclared source dependency"),
        reject("missing_reader", lambda: audit_code(changed(readers=1022)), "decoder collision"),
        reject("truncated_output", lambda: audit_code(changed(width=4, outputs=tuple(y & 15 for y in binary.messages[0].outputs))), "decoder collision"),
        reject("altered_output", lambda: audit_code(changed(outputs=(1,) + binary.messages[0].outputs[1:])), "decoder collision"),
    ]
    # Outside the side-information premise, the claimed floor is false:
    # one parity bit, known to all, suffices if every other input is free.
    parity = changed(width=1, outputs=tuple(sum(x) % 2 for x in states(binary.widths)))
    controls.append(reject("extra_side_information_not_granted", lambda: audit_code(parity), "decoder collision"))
    boundary = audit_code(parity, extra_side_information=True)
    require(boundary["cost"] == 2 < boundary["floor"] == 10, "boundary counterexample")
    budgets = []
    for b, s in product((1, 2, 7), (1, 3, 5, 9, 31)):
        deficit = (s - 1) * 40 * b - s * 40 * b
        require(deficit == -40 * b, "Dfc identity")
        budgets.append([b, s, deficit])
    sources_digest = sha256((HERE / "SOURCES.json").read_bytes()).hexdigest()
    return {"schema": 1, "sources_manifest_sha256": sources_digest,
            "geometry": geo, "local_certificate": local, "attaining_examples": examples,
            "negative_controls": controls, "outside_model_extra_side_information": boundary,
            "conditional_budget_examples_b_s_deficit": budgets,
            "scope": "Fixed support, fixed width, zero error, independent inputs, q*c additive pricing; written all-width proof in PROOF.md"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="explicitly write a newly computed receipt")
    parser.add_argument("--check", type=Path, default=HERE / "RESULTS.json")
    args = parser.parse_args()
    result = build_receipt()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        require(args.check.read_text() == encoded, "committed receipt differs")
    print("PASS_HURWITZ_NONLINEAR_COPY: 1048576 support pairs; 3 attaining codes; "
          "12 rejection controls; conditional floor 10b")


if __name__ == "__main__":
    main()
