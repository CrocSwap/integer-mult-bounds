#!/usr/bin/env python3
"""Check literal star decoders and spanning identities, without elimination.

Python 3.10+, standard library only. Apache-2.0.
Prepared for ellipsi2 with substantial OpenAI Codex assistance.
"""

import argparse
import copy
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOMAINS = [(p, k) for k in (2, 3, 4) for p in range(k, 9)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry(p, k, include_empty):
    """Independent ternary-word enumeration; builder uses combinations/signs."""
    ports, stars = set(), set()
    for word in itertools.product((0, 1, 2), repeat=p):
        degree = sum(symbol != 0 for symbol in word)
        if degree > k:
            continue
        mask = sum(1 << (2 * i + symbol - 1)
                   for i, symbol in enumerate(word) if symbol)
        if degree == k:
            ports.add(mask)
        elif degree or include_empty:
            stars.add(mask)
    return ports, stars


def xor_selected(values, selector):
    result = 0
    while selector:
        bit = selector & -selector
        result ^= values[bit.bit_length() - 1]
        selector -= bit
    return result


def rank_formula(p, k, include_empty):
    rho = sum(comb(p, j) * comb(p - j, min(k - 1 - j, p - k))
              for j in range(k))
    constant_missing = (k & (k - 1) == 0) and p >= 2 * k - 1
    return rho - int(constant_missing and not include_empty)


def check_case(case):
    p, k, empty = case["p"], case["k"], case["include_empty"]
    require(type(p) is int and type(k) is int and (p, k) in DOMAINS,
            "outside declared domain")
    require(type(empty) is bool, "empty-star flag must be Boolean")
    actual_ports, actual_stars = geometry(p, k, empty)
    ports, stars, info = case["ports"], case["stars"], case["information_set"]
    for values, expected, name in ((ports, actual_ports, "ports"),
                                   (stars, actual_stars, "stars")):
        require(all(type(value) is int for value in values), name + " not integers")
        require(len(values) == len(expected) and set(values) == expected,
                name + " incomplete, duplicated or invalid")
    require(all(type(value) is int for value in info), "invalid information set")
    require(len(info) == len(set(info)) and set(info) <= actual_ports,
            "information set duplicated or invalid")
    encoded = case["decoders_hex"]
    require(len(encoded) == len(info), "decoder count differs")
    coefficients = []
    for value in encoded:
        require(type(value) is str, "decoder encoding must be a string")
        decoded = int(value, 16)
        require(decoded >= 0 and decoded < 1 << len(stars) and hex(decoded) == value,
                "noncanonical or out-of-range decoder")
        coefficients.append(decoded)

    position = {port: i for i, port in enumerate(ports)}
    information_positions = [position[port] for port in info]
    information_mask = sum(1 << i for i in information_positions)
    rows = [sum(1 << col for col, port in enumerate(ports) if port & star == star)
            for star in stars]
    decoders = [xor_selected(rows, c) for c in coefficients]

    # Every decoder is an explicit available-star combination; its restriction
    # to the information set is one particular unit vector. This proves the
    # lower rank bound and gives all attaining scalar decoders.
    for col, row in zip(information_positions, decoders):
        require(row & information_mask == 1 << col,
                "decoder is not its claimed unit vector")

    # The upper rank bound is a literal identity on ALL original ports for
    # EVERY allowed generator, not just a reported Gaussian-elimination rank.
    for star, row in zip(stars, rows):
        expansion = 0
        for port, decoder in zip(info, decoders):
            if port & star == star:
                expansion ^= decoder
        require(expansion == row, "star not spanned on the full port family")

    rank = len(info)
    require(rank == rank_formula(p, k, empty), "uniform rank formula differs")
    return {
        "p": p, "k": k, "include_empty": empty,
        "ports": len(ports), "stars": len(stars), "rank": rank,
        "all_star_identities": len(stars), "unit_decoders": rank,
        "minimum_deletions_for_star_only_all_target": len(ports) - rank,
    }


def check_corrections(p, k):
    ports, _ = geometry(p, k, False)
    ports = sorted(ports)
    count = 0
    for target in ports:
        # Binomial polynomials of positive degree, indexed by overlap r.
        tables = [[comb(r, degree) & 1 for r in range(k + 1)]
                  for degree in range(1, k)]
        if k & (k - 1) == 0:
            for overlap in range(1, k):
                remaining = [int(r == overlap) for r in range(k + 1)]
                chosen = []
                for degree in range(1, k):
                    if remaining[degree]:
                        chosen.append(degree)
                        remaining = [a ^ b for a, b in zip(remaining, tables[degree - 1])]
                require(not any(remaining), "overlap correction has forbidden endpoint")
                # Verify every actual source, including disjoint and target.
                for source in ports:
                    r = (source & target).bit_count()
                    require(sum(comb(r, d) for d in chosen) % 2 == (r == overlap),
                            "correction absorption failed")
                count += 1
        elif k == 3:
            # A positive escape control: corrections CAN add target singletons.
            for source in ports:
                r = (source & target).bit_count()
                require(((r & 1) ^ int(r == 1)) == int(source == target),
                        "non-power-of-two escape failed")
            count += 1
    return count


def check_document(document):
    require(document["format"] == "signed-star-information-sets-v1", "format differs")
    require(document["assignment_seed"] == 46 and document["principal_domain"] == [8, 4],
            "assignment differs")
    cases = document["cases"]
    require([(c["p"], c["k"], c["include_empty"]) for c in cases]
            == [(p, k, empty) for p, k in DOMAINS for empty in (False, True)],
            "case coverage differs")
    return [check_case(case) for case in cases]


def negative_controls(document):
    principal = next(c for c in document["cases"]
                     if (c["p"], c["k"], c["include_empty"]) == (8, 4, False))
    mutants = []
    case = copy.deepcopy(principal)
    case["decoders_hex"][0] = hex(int(case["decoders_hex"][0], 16) ^ 1)
    mutants.append(("wrong decoder coefficient", case))
    case = copy.deepcopy(principal)
    case["information_set"][0] = case["information_set"][1]
    mutants.append(("duplicate retained port", case))
    case = copy.deepcopy(principal)
    case["stars"][0] = case["ports"][0]
    mutants.append(("degree-k singleton supplied as proper star", case))
    case = copy.deepcopy(principal)
    case["stars"][0] = 0
    mutants.append(("unpaid global sum in nonempty class", case))
    case = copy.deepcopy(principal)
    case["ports"][0] ^= 1
    mutants.append(("changed source coordinate", case))
    case = copy.deepcopy(principal)
    case["decoders_hex"].pop()
    mutants.append(("missing decoder", case))
    # Removing an information coordinate AND its decoder preserves every
    # remaining unit-vector equation. Only the full-family spanning obligation
    # detects this false upper-rank certificate.
    case = copy.deepcopy(principal)
    case["information_set"].pop()
    case["decoders_hex"].pop()
    mutants.append(("false rank with valid remaining decoders", case))
    for name, case in mutants:
        try:
            check_case(case)
        except ValueError as error:
            if name == "false rank with valid remaining decoders":
                require(str(error) == "star not spanned on the full port family",
                        "false-rank control did not reach the spanning obligation")
            continue
        raise ValueError("negative control accepted: " + name)
    incomplete = copy.deepcopy(document)
    incomplete["cases"].pop()
    try:
        check_document(incomplete)
    except ValueError:
        pass
    else:
        raise ValueError("negative control accepted: missing case")
    return [name for name, _ in mutants] + ["missing case"]


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    root = HERE.parents[1]
    for name, expected in sources["local_context_sha256"].items():
        candidate = (root / name).resolve()
        require(candidate.is_relative_to(root.resolve()), "source escapes root")
        require(hashlib.sha256(candidate.read_bytes()).hexdigest() == expected,
                "context source changed: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write", type=Path, help="export only after all checks pass")
    args = parser.parse_args()
    check_sources()
    document = json.loads(args.certificate.read_text(encoding="utf-8"))
    cases = check_document(document)
    controls = negative_controls(document)
    correction_checks = [
        {"p": p, "k": k, "target_correction_checks": check_corrections(p, k)}
        for p, k in DOMAINS
    ]
    result = {
        "status": "PASS_PAIRED_STAR_RANK",
        "cases": cases,
        "corrections_and_escape_controls": correction_checks,
        "negative_controls": controls,
        "kappa": "unchanged",
    }
    expected = json.loads((HERE / "RESULTS.json").read_text(encoding="utf-8"))
    require(result == expected, "complete deterministic receipt differs")
    if args.write:
        args.write.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print("PASS_PAIRED_STAR_RANK: 36 cases; (8,4) ranks 447/448; "
          "all-target deletions 673/672; 8 negative controls; kappa unchanged")


if __name__ == "__main__":
    main()
