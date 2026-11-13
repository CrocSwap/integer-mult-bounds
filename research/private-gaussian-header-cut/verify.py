"""Exact private-header transcript evidence; no predecessor or geometry replay."""

import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def project(value, mask, width):
    return tuple((value >> i) & 1 for i in range(width) if mask >> i & 1)


def source_index(value, mask, width):
    return sum(bit << i for i, bit in enumerate(project(value, mask, width)))


def prefix_check(code):
    require(len(code) == len(set(code)), "duplicate header codeword")
    require(all(set(word) <= {"0", "1"} for word in code), "nonbinary code")
    require(all(not b.startswith(a) for i, a in enumerate(code)
                for j, b in enumerate(code) if i != j), "nonprefix code")


def validate(width, sources, readers, table, code):
    require(type(width) is int and 1 <= width <= 6, "unsupported width")
    require(type(sources) is int and 0 < sources < 1 << width, "bad sources")
    require(type(readers) is int and 0 < readers < 1 << width, "bad readers")
    require(len(table) == 1 << sources.bit_count(), "bad header table")
    require(all(type(m) is int and 0 <= m < len(code) for m in table),
            "bad header value")
    prefix_check(code)


def make_branches(width, sources, readers, header):
    branches = {}
    for message in sorted(set(header)):
        fiber = tuple(x for x, m in enumerate(header) if m == message)
        payloads, known = [], {}
        for target in range(width):
            values = {(x >> target) & 1 for x in fiber}
            if readers >> target & 1:
                if len(values) == 1:
                    known[target] = next(iter(values))
                else:
                    payloads.append((target, sources | (1 << target), True))
            else:
                payloads.append((target, 1 << target, False))
        branches[message] = (tuple(payloads), known)
    return branches


def check_locality(sources, readers, branches):
    fixed = None
    for payloads, _ in branches.values():
        current = []
        for target, support, adaptive in payloads:
            if adaptive:
                require(readers >> target & 1, "private schedule escaped readers")
                require(support & sources == sources, "encoder lacks header sources")
            else:
                current.append((target, support))
        if fixed is None:
            fixed = tuple(current)
        require(tuple(current) == fixed, "fixed schedule depends on header")


def check_receivers(width, readers, header, branches):
    observations = [dict() for _ in range(width)]
    checks = 0
    for x, message in enumerate(header):
        payloads, known = branches[message]
        sent = {target: ((x >> target) & 1) ^ (message & 1 if adaptive else 0)
                for target, _, adaptive in payloads}
        for target in range(width):
            private = bool(readers >> target & 1)
            key = (message if private else None, sent.get(target))
            bit = (x >> target) & 1
            old = observations[target].setdefault(key, bit)
            require(old == bit, "receiver collision")
            decoded = known.get(target) if private and target in known else (
                sent[target] ^ (message & 1 if private else 0))
            require(decoded == bit, "literal decode differs")
            checks += 1
    return checks


def entropy_product(header, outside, width):
    counts = Counter((project(x, outside, width), m)
                     for x, m in enumerate(header))
    result = 1
    for count in counts.values():
        result *= count ** count
    return result


def check_cuts(width, sources, readers, header, branches):
    full = (1 << width) - 1
    outcomes = Counter()
    for cut in range(1, 1 << width):
        joint = bool(cut & sources and cut & readers)
        retained = sum(sum(bool(cut >> target & 1 and support & cut)
                           for target, support, _ in branches[m][0])
                       for m in header)
        if joint:
            # H(M|outside) = |cut| - log2(product fiber_size^fiber_size)/N.
            require(entropy_product(header, full ^ cut, width) <= 2 ** retained,
                    "joint private-header cut bound failed")
        else:
            require(retained >= len(header) * cut.bit_count(),
                    "cut needs an unobserved header")
        outcomes["joint" if joint else "no_joint"] += 1
    return outcomes


def protocol_case(width, sources, readers, table, code):
    validate(width, sources, readers, table, code)
    header = tuple(table[source_index(x, sources, width)] for x in range(1 << width))
    branches = make_branches(width, sources, readers, header)
    check_locality(sources, readers, branches)
    checks = check_receivers(width, readers, header, branches)
    cuts = check_cuts(width, sources, readers, header, branches)
    length = Fraction(sum(len(code[m]) for m in header), len(header))
    payload = Fraction(sum(len(branches[m][0]) for m in header), len(header))
    return checks, cuts, str(length), str(payload)


def binary_corpus():
    totals = Counter()
    for sources in range(1, 8):
        size = 1 << sources.bit_count()
        for table in product((0, 1), repeat=size):
            for readers in range(1, 8):
                checks, cuts, _, _ = protocol_case(3, sources, readers, table, ("0", "1"))
                totals["protocols"] += 1
                totals["receiver_checks"] += checks
                totals.update(cuts)
    return dict(totals)


def gaussian_examples():
    # Source F in the cited rank-one pair meets reader G at active indices 0,5.
    parity = tuple(x.bit_count() & 1 for x in range(64))
    nonlinear = tuple((x & 1) ^ (((x >> 1) & 1) & ((x >> 2) & 1))
                      for x in range(64))
    ternary = tuple(0 if x & 3 == 0 else 1 if x & 3 == 1 else 2
                    for x in range(64))
    cases = (("parity", parity, ("0", "1")),
             ("nonlinear", nonlinear, ("0", "1")),
             ("variable_prefix", ternary, ("0", "10", "11")))
    result = {}
    for name, table, code in cases:
        checks, cuts, length, payload = protocol_case(6, 63, 33, table, code)
        result[name] = {"receiver_checks": checks, "cuts": dict(cuts),
                        "header_length": length, "payload_charge": payload,
                        "total_charge": str(Fraction(length) + Fraction(payload))}
    return result


def rejected_controls():
    rejected = []
    for code in (("0", "01"), ("0", "0"), ("2", "1")):
        try:
            prefix_check(code)
        except ValueError:
            rejected.append("invalid_prefix")
        else:
            raise ValueError("prefix mutation survived")
    mutations = (
        {0: (((0, 3, True),), {})},
        {0: (((1, 2, True),), {})},
        {0: (((0, 1, False),), {}), 1: ((), {})},
    )
    for branches in mutations:
        try:
            check_locality(1, 2, branches)
        except ValueError:
            rejected.append("invalid_visibility_or_encoder")
        else:
            raise ValueError("locality mutation survived")
    try:
        check_receivers(1, 1, (0, 0), {0: ((), {})})
    except (KeyError, ValueError):
        rejected.append("missing_payload")
    else:
        raise ValueError("missing payload survived")
    return rejected


def leakage_witness():
    observations = ((), ("",))
    require(observations[0] != observations[1], "leakage witness lost")
    require(sum(len(word) for obs in observations for word in obs) == 0,
            "leakage witness paid data")
    return {"inputs": 2, "payload_bits": 0, "distinct_outside_observations": 2}


def main():
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    package = Path(__file__).resolve().parent
    receipt = {"status": "PASS_PRIVATE_GAUSSIAN_HEADER_CUT",
               "binary_corpus": binary_corpus(),
               "gaussian_protocols": gaussian_examples(),
               "rejected_controls": rejected_controls(),
               "outside_schedule_leak": leakage_witness()}
    files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in files:
        path = package / name
        require(path.stat().st_size <= 1 << 20, "oversized package source")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt["source_sha256"] = hashes
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
