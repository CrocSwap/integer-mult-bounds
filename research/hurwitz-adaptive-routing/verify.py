#!/usr/bin/env python3
"""Exact controls for a scoped adaptive-header theorem; Python 3.10+, stdlib.

No supplier implementation or full multiplication theorem is verified here.
Run without arguments to compare the complete replay with CERTIFICATE.json.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
from typing import Callable


ROOT = Path(__file__).resolve().parent
SEED = 42


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rref(rows: list[tuple[int, ...]]) -> tuple[tuple[Fraction, ...], ...]:
    a = [[Fraction(v) for v in row] for row in rows]
    if not a:
        return ()
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        value = a[pivot][col]
        a[pivot] = [v / value for v in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return tuple(tuple(row) for row in a[:pivot])


def left_multiples(v: tuple[int, ...]) -> list[tuple[int, ...]]:
    transforms = (
        lambda a, b, c, d: (a, b, c, d),
        lambda a, b, c, d: (-b, a, -d, c),
        lambda a, b, c, d: (-c, d, a, -b),
        lambda a, b, c, d: (-d, -c, b, a),
    )
    return [fn(*v[:4]) + fn(*v[4:]) for fn in transforms]


def geometry() -> tuple[list[int], dict]:
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = a, b
            roots.add(tuple(v))
    roots.update(v for v in product((-1, 1), repeat=8) if sum(x < 0 for x in v) % 2 == 0)
    require(len(roots) == 240, "root count")
    lines: dict[tuple, list[tuple[int, ...]]] = {}
    root_counts: Counter = Counter()
    for root in sorted(roots):
        require(sum(x * x for x in root) == 8, "root norm")
        rows = left_multiples(root)
        require(all(row in roots for row in rows), "quaternionic closure")
        key = rref(rows)
        require(len(key) == 4, "line dimension")
        lines.setdefault(key, rows)
        root_counts[key] += 1
    require(len(lines) == 10 and set(root_counts.values()) == {24}, "line partition")
    bases = list(lines.values())
    mates: list[int] = []
    pairing_ranks = []
    for i, a in enumerate(bases):
        ranks = []
        for b in bases:
            gram = [tuple(sum(x * y for x, y in zip(u, v)) for v in b) for u in a]
            ranks.append(len(rref(gram)))
        orthogonal = [j for j, rank in enumerate(ranks) if rank == 0]
        require(len(orthogonal) == 1 and i not in orthogonal, "unique orthogonal mate")
        require(set(ranks) == {0, 4}, "singleton pairing rank")
        mates.append(orthogonal[0])
        pairing_ranks.append(ranks)
    require(all(mates[mates[i]] == i for i in range(10)), "mate involution")
    for i, j in combinations(range(10), 2):
        require(len(rref(bases[i] + bases[j])) == 8, "two lines span ambient space")
    return mates, {
        "roots": len(roots), "lines": len(lines), "roots_per_line": 24,
        "line_bases": bases, "mates": mates, "singleton_pairing_ranks": pairing_ranks,
        "two_line_spans_checked": 45,
    }


def charge(readers: int, sources: int, mates: list[int]) -> int:
    if not readers or not sources:
        return 0
    if readers.bit_count() == sources.bit_count() == 1:
        r, a = readers.bit_length() - 1, sources.bit_length() - 1
        return int(mates[r] != a)
    return 1 if min(readers.bit_count(), sources.bit_count()) == 1 else 2


def transversal_check(mates: list[int]) -> dict:
    pairs = [(i, m) for i, m in enumerate(mates) if i < m]
    transversals = [sum(1 << i for i in choice) for choice in product(*pairs)]
    require(len(transversals) == 32 and len(set(transversals)) == 32, "transversal count")
    require(all(sum(bool(t & (1 << i)) for t in transversals) == 16 for i in range(10)),
            "transversal incidence")
    hits = [sum(1 << j for j, t in enumerate(transversals) if mask & t) for mask in range(1024)]
    counts: Counter = Counter()
    max_hits = [0, 0, 0]
    for a in range(1024):
        for r in range(1024):
            c = charge(r, a, mates)
            h = (hits[a] & hits[r]).bit_count()
            require(h <= 16 * c, "transversal geometric inequality")
            counts[c] += 1
            max_hits[c] = max(max_hits[c], h)
    return {"transversals": transversals, "support_pairs": sum(counts.values()),
            "charge_counts": dict(sorted(counts.items())), "max_joint_hits_by_charge": max_hits}


def projection(x: int, coordinates: tuple[int, ...]) -> int:
    return sum(((x >> p) & 1) << j for j, p in enumerate(coordinates))


def anf_terms(function: int) -> list[int]:
    coefficients = [(function >> x) & 1 for x in range(16)]
    for bit in range(4):
        for x in range(16):
            if x & (1 << bit):
                coefficients[x] ^= coefficients[x ^ (1 << bit)]
    return [i for i, coefficient in enumerate(coefficients) if coefficient]


def raw_pair_works(fibre: int, source_pair: tuple[int, int]) -> bool:
    for target in range(4):
        decoded = {}
        for x in range(16):
            if not (fibre >> x) & 1:
                continue
            key = (projection(x, source_pair), (x >> (target ^ 1)) & 1)
            value = (x >> target) & 1
            if key in decoded and decoded[key] != value:
                return False
            decoded[key] = value
    return True


def census() -> dict:
    transversals = list(product((0, 1), (2, 3)))
    slices = []
    for t in transversals:
        outside = tuple(i for i in range(4) if i not in t)
        slices.append([sum(1 << x for x in range(16) if projection(x, outside) == u)
                       for u in range(4)])
    # All possible fibres, including empty and full, are computed once.
    branch_bounds = []
    for fibre in range(65536):
        if not fibre:
            branch_bounds.append(0)
            continue
        bits = sum((max((fibre & s).bit_count() for s in group) - 1).bit_length()
                   for group in slices)
        branch_bounds.append((bits + 1) // 2)
    require(branch_bounds[0] == 0 and branch_bounds[65535] == 4, "constant-header baseline")
    histogram: Counter = Counter()
    attaining = []
    for function in range(1, 65535):
        fibres = [65535 ^ function, function]
        numerator = sum(f.bit_count() * branch_bounds[f] for f in fibres)
        require(numerator >= 32, "paid adaptive header floor")
        histogram[numerator] += 1
        if numerator != 32:
            continue
        witnesses = []
        for fibre in fibres:
            candidates = [pair for pair in combinations(range(4), 2) if raw_pair_works(fibre, pair)]
            require(bool(candidates), "lower-bound equality lacks an attaining decoder")
            witnesses.append(candidates)
        terms = anf_terms(function)
        attaining.append({"truth_table": function, "fibre_sizes": [f.bit_count() for f in fibres],
                          "branch_payload_lower_bounds": [branch_bounds[f] for f in fibres],
                          "raw_source_pairs_by_header": witnesses, "anf_terms": terms,
                          "nonlinear": any(t.bit_count() > 1 for t in terms)})
    require(len(attaining) == 30, "optimal header classification")
    return {
        "domain": "all Boolean functions of four one-bit inputs; pairs (0,1),(2,3)",
        "functions_checked": 65536, "nonconstant_functions": 65534,
        "constant_headers": {"functions": [0, 65535], "one_bit_header_lower_cost": 6,
                             "empty_header_optimum_cost": 4},
        "expected_payload_lower_bound_numerator_over_16": dict(sorted(histogram.items())),
        "optimal_nonconstant_headers": attaining,
        "nonlinear_optimal_headers": sum(row["nonlinear"] for row in attaining),
        "attaining_receiver_decodes": 30 * 16 * 4,
        "stopping_rule": "exhaust all 65536 truth tables, then verify every equality witness",
    }


@dataclass(frozen=True)
class Message:
    sources: int
    readers: int
    value: int
    width: int = 1


Protocol = Callable[[int], tuple[str, tuple[Message, ...]]]


def prefix_free(words: set[str]) -> bool:
    ordered = sorted(words)
    return all(not b.startswith(a) for a, b in zip(ordered, ordered[1:]))


def check_protocol(protocol: Protocol, mates: list[int], *, allow_nonprefix: bool = False) -> dict:
    n = len(mates)
    signatures = {}
    encodings = {}
    receivers = [{} for _ in mates]
    costs: Counter = Counter()
    headers: Counter = Counter()
    for x in range(1 << n):
        header, messages = protocol(x)
        require(set(header) <= {"0", "1"}, "nonbinary header")
        signature = tuple((m.sources, m.readers, m.width) for m in messages)
        if header in signatures:
            require(signatures[header] == signature, "routing choices not determined by header")
        signatures[header] = signature
        headers[header] += 1
        cost = 2 * len(header)
        for j, m in enumerate(messages):
            require(0 <= m.sources < 1 << n and 0 <= m.readers < 1 << n, "invalid supports")
            require(m.width >= 0 and 0 <= m.value < 1 << m.width, "payload exceeds fixed width")
            source_key = (header, j, x & m.sources)
            if source_key in encodings:
                require(encodings[source_key] == m.value, "payload depends on undeclared source")
            encodings[source_key] = m.value
            cost += m.width * charge(m.readers, m.sources, mates)
        for t in range(n):
            key = (header, (x >> mates[t]) & 1,
                   tuple(m.value for m in messages if (m.readers >> t) & 1))
            value = (x >> t) & 1
            if key in receivers[t]:
                require(receivers[t][key] == value, f"decode collision at receiver {t}")
            receivers[t][key] = value
        costs[cost] += 1
    require(allow_nonprefix or prefix_free(set(headers)), "header code is not prefix-free")
    expected_cost = Fraction(sum(c * count for c, count in costs.items()), 1 << n)
    return {"inputs": 1 << n, "receiver_decodes": n * (1 << n),
            "headers": dict(sorted(headers.items())), "cost_histogram": dict(sorted(costs.items())),
            "expected_cost": str(expected_cost), "max_cost": max(costs)}


def examples(mates: list[int], census_result: dict) -> tuple[dict, dict]:
    pairs = [(i, m) for i, m in enumerate(mates) if i < m]
    rng = random.Random(SEED)
    rng.shuffle(pairs)
    complement = rng.randrange(2)
    all_ports = (1 << len(mates)) - 1

    def parity(x: int, pair: tuple[int, int]) -> int:
        return ((x >> pair[0]) ^ (x >> pair[1])) & 1

    def pair_message(x: int, pair: tuple[int, int]) -> Message:
        mask = sum(1 << i for i in pair)
        return Message(mask, mask, parity(x, pair))

    def adaptive(x: int) -> tuple[str, tuple[Message, ...]]:
        route = parity(x, pairs[0]) ^ parity(x, pairs[1]) ^ complement
        chosen = pairs[route]
        messages = [Message(1 << i, all_ports, (x >> i) & 1) for i in chosen]
        messages.extend(pair_message(x, pair) for pair in pairs[2:])
        return str(route), tuple(messages)

    def variable(x: int) -> tuple[str, tuple[Message, ...]]:
        z = [parity(x, pair) for pair in pairs]
        if z[0] == 0:
            header, start = "0", 1
        else:
            header, start = "1" + str(z[1]), 2
        return header, tuple(pair_message(x, pair) for pair in pairs[start:])

    nonlinear_row = rng.choice([r for r in census_result["optimal_nonconstant_headers"] if r["nonlinear"]])
    function = nonlinear_row["truth_table"]

    def nonlinear(x: int) -> tuple[str, tuple[Message, ...]]:
        r = (function >> x) & 1
        source_pair = nonlinear_row["raw_source_pairs_by_header"][r][0]
        return str(r), tuple(Message(1 << i, 15, (x >> i) & 1) for i in source_pair)

    def bad_prefix(x: int) -> tuple[str, tuple[Message, ...]]:
        header = "0" if parity(x, pairs[0]) else ""
        return header, tuple(pair_message(x, pair) for pair in pairs[1:])

    def nonpointwise(x: int) -> tuple[str, tuple[Message, ...]]:
        z = "".join(str(parity(x, pair)) for pair in pairs)
        return ("0" if z == "00000" else "1" + z), ()

    results = {"seed": SEED, "ordered_actual_pairs": pairs, "parity_complement": complement,
               "adaptive_ten_ports": check_protocol(adaptive, mates),
               "variable_header_ten_ports": check_protocol(variable, mates),
               "valid_nonpointwise_ten_ports": check_protocol(nonpointwise, mates),
               "nonlinear_four_port_header": function,
               "nonlinear_four_ports": check_protocol(nonlinear, [1, 0, 3, 2])}
    require(results["adaptive_ten_ports"]["expected_cost"] == "10", "adaptive attainment")
    require(results["variable_header_ten_ports"]["expected_cost"] == "10", "prefix attainment")
    require(results["nonlinear_four_ports"]["expected_cost"] == "4", "nonlinear attainment")
    require(results["valid_nonpointwise_ten_ports"]["cost_histogram"] == {2: 32, 12: 992},
            "expected-cost theorem must not become a pointwise claim")

    rejected = []

    def rejects(name: str, operation: Callable[[], object], expected: str) -> None:
        try:
            operation()
        except ValueError as exc:
            require(expected in str(exc), f"wrong failure for {name}: {exc}")
            rejected.append({"name": name, "reason": str(exc)})
        else:
            raise ValueError(f"negative control accepted: {name}")

    def drop_payload(x: int) -> tuple[str, tuple[Message, ...]]:
        header, messages = adaptive(x)
        return header, messages[1:]

    def underdeclare(x: int) -> tuple[str, tuple[Message, ...]]:
        header, messages = adaptive(x)
        first = messages[0]
        return header, (Message(0, first.readers, first.value),) + messages[1:]

    def hidden_routing(x: int) -> tuple[str, tuple[Message, ...]]:
        _, messages = adaptive(x)
        return "0", messages

    def oversized(x: int) -> tuple[str, tuple[Message, ...]]:
        header, messages = adaptive(x)
        first = messages[0]
        return header, (Message(first.sources, first.readers, 2),) + messages[1:]

    rejects("dropped source bit", lambda: check_protocol(drop_payload, mates), "decode collision")
    rejects("undeclared payload source", lambda: check_protocol(underdeclare, mates), "undeclared source")
    rejects("hidden routing metadata", lambda: check_protocol(hidden_routing, mates), "routing choices")
    rejects("payload width omitted", lambda: check_protocol(oversized, mates), "fixed width")
    rejects("free termination information", lambda: check_protocol(bad_prefix, mates), "prefix-free")
    bad_prefix_result = check_protocol(bad_prefix, mates, allow_nonprefix=True)
    require(bad_prefix_result["expected_cost"] == "9", "nonprefix boundary example")
    boundary = {
        "free_header_adaptive_expected_cost": "8",
        "rank_one_priced_header_adaptive_expected_cost": "9",
        "nonprefix_free_termination": bad_prefix_result,
        "interpretation": "correct decoding outside pricing/prefix premises, not counterexamples to the theorem",
    }
    # The adaptive example sends one header bit on every input, so subtracting
    # its two-unit price gives the exact free/underpriced-header boundaries.
    paid = Fraction(results["adaptive_ten_ports"]["expected_cost"])
    require(paid - 2 == Fraction(boundary["free_header_adaptive_expected_cost"]), "free header price")
    require(paid - 1 == Fraction(boundary["rank_one_priced_header_adaptive_expected_cost"]), "underpriced header")
    return results, {"rejected": rejected, "boundary_examples": boundary}


def check_sources() -> str:
    manifest_path = ROOT / "SOURCES.json"
    manifest = json.loads(manifest_path.read_text())
    for source in manifest["retained_sources"]:
        data = (ROOT / source["local_path"]).read_bytes()
        require(sha256(data).hexdigest() == source["sha256"], f"source digest mismatch: {source['local_path']}")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(sha1(blob).hexdigest() == source["git_blob_sha1"], f"source Git blob mismatch: {source['local_path']}")
    return sha256(manifest_path.read_bytes()).hexdigest()


def calculate() -> dict:
    manifest_digest = check_sources()
    mates, geo = geometry()
    transversals = transversal_check(mates)
    header_census = census()
    code_examples, controls = examples(mates, header_census)
    return {"schema": "hurwitz-adaptive-routing-v1", "seed": SEED,
            "base_commit": "f567884aeb8851b6e794af1184119a3bfbe1e631",
            "sources_sha256": manifest_digest, "geometry": geo,
            "transversal_certificate": transversals, "four_port_census": header_census,
            "protocol_examples": code_examples, "controls": controls,
            "result": "E[2 header_length + payload_charge] >= sum demand_bits; no new kappa"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a freshly regenerated certificate to an explicit path")
    args = parser.parse_args()
    result = calculate()
    serialized = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write is not None:
        args.write.write_text(serialized)
    else:
        require(serialized == (ROOT / "CERTIFICATE.json").read_text(), "certificate differs from exact replay")
    print("PASS_HURWITZ_ADAPTIVE_ROUTING support_pairs=1048576 boolean_headers=65536 "
          "optimal_nonconstant_headers=30 floor=10b no_new_kappa")


if __name__ == "__main__":
    main()
