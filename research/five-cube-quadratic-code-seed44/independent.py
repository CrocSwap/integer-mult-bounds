#!/usr/bin/env python3
"""Check the finite proof without importing the generator or running Dijkstra.

Uses coordinate sets, Boolean polynomials, Fraction elimination and edge
potentials. Hanson Sun (@bbMisk), substantial OpenAI Codex assistance.
Apache-2.0. A separate implementation is not independent human review.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

DIRECTORY = Path(__file__).resolve().parent
PAIRS = tuple(combinations(range(5), 2))
MONOMIAL_ORDER = tuple((i,) for i in range(4)) + PAIRS


def check(condition, message):
    if not condition:
        raise ValueError(message)


def exact_rank(matrix):
    if not matrix:
        return 0
    rows = [[Fraction(entry) for entry in row] for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        selected = next((k for k in range(pivot_row, len(rows)) if rows[k][column]), None)
        if selected is None:
            continue
        rows[selected], rows[pivot_row] = rows[pivot_row], rows[selected]
        scale = rows[pivot_row][column]
        for j in range(column, len(rows[0])):
            rows[pivot_row][j] /= scale
        for k in range(pivot_row + 1, len(rows)):
            factor = rows[k][column]
            if factor:
                for j in range(column, len(rows[0])):
                    rows[k][j] -= factor * rows[pivot_row][j]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def polynomial(code):
    return {term for bit, term in enumerate(MONOMIAL_ORDER) if code & (2**bit)}


def transform(code, generator):
    terms = polynomial(code)
    if generator < 5:
        # Substitute x_i+1 for x_i directly in the algebraic normal form.
        terms ^= {tuple(j for j in term if j != generator)
                  for term in tuple(terms) if generator in term}
    else:
        i = generator - 5
        rename = {i: i + 1, i + 1: i}
        terms = {tuple(sorted(rename.get(j, j) for j in term)) for term in terms}
    terms.discard(())  # Quotient by the constant function.
    if (4,) in terms:
        terms ^= {(j,) for j in range(5)}  # Quotient by parity.
    check(all(term in MONOMIAL_ORDER for term in terms), "transformation left quadratic domain")
    return sum(2**MONOMIAL_ORDER.index(term) for term in terms)


def geometry():
    orientations = [tuple((address // (2**i)) % 2 for i in range(5))
                    for address in range(32)]
    ports = [{2 * i + orientation[i] for i in range(5)} for orientation in orientations]
    gram = [[2 * (len(s & t) - 1) * (len(s & t) - 3) for t in ports] for s in ports]
    parity = [sum(x) % 2 for x in orientations]
    decoder = [[int(parity[i] == parity[j]) for j in range(32)] for i in range(32)]
    return orientations, gram, parity, decoder


def masks_for_domain(orientations, parity):
    full_terms = ((),) + tuple((i,) for i in range(5)) + PAIRS
    evaluations = [sum(int(all(x[i] for i in term)) * (2**address)
                       for address, x in enumerate(orientations)) for term in full_terms]
    full = (2**32) - 1
    odd = sum(bit * (2**i) for i, bit in enumerate(parity))
    all_masks = [0] * (2**16)
    quotient_counts = Counter()
    for coefficient in range(2**16):
        if coefficient:
            bit = coefficient.bit_length() - 1
            all_masks[coefficient] = all_masks[coefficient - 2**bit] ^ evaluations[bit]
        h = all_masks[coefficient]
        quotient_counts[min(h, h ^ full, h ^ odd, h ^ full ^ odd)] += 1
    check(len(set(all_masks)) == 65536, "full quadratic evaluation has a kernel")
    check(len(quotient_counts) == 16384 and set(quotient_counts.values()) == {4},
          "incomplete quotient domain")
    quotient_masks = []
    keys = set()
    for code in range(16384):
        h = 0
        for term in polynomial(code):
            h ^= evaluations[full_terms.index(term)]
        key = min(h, h ^ full, h ^ odd, h ^ full ^ odd)
        check(key in quotient_counts and key not in keys, "duplicate or absent quotient code")
        keys.add(key)
        quotient_masks.append(h)
    return quotient_masks


def check_isometries(orientations, gram, decoder):
    for generator in range(9):
        image = []
        for x in orientations:
            y = list(x)
            if generator < 5:
                y[generator] = 1 - y[generator]
            else:
                i = generator - 5
                y[i], y[i + 1] = y[i + 1], y[i]
            image.append(orientations.index(tuple(y)))
        check(len(set(image)) == 32, "non-bijective proposed symmetry")
        for x in range(32):
            for y in range(32):
                check(gram[x][y] == gram[image[x]][image[y]] and
                      decoder[x][y] == decoder[image[x]][image[y]],
                      "proposed symmetry does not preserve the model")


def check_transports(certificate):
    owners = {}
    roots = set()
    for child, parent, generator, root in certificate["transports"]:
        check(type(child) is int and 1 <= child < 16384 and child not in owners,
              "missing/duplicate/invalid transport node")
        if parent == 0:
            check(generator == -1 and root == child, "invalid transport root")
            roots.add(root)
        else:
            check(parent in owners and owners[parent] == root and 0 <= generator < 9,
                  "transport parent is not established")
            check(transform(parent, generator) == child, "false polynomial symmetry transport")
        owners[child] = root
    check(set(owners) == set(range(1, 16384)), "quadratic coverage omitted")
    check(len(roots) == 64, "wrong number of roots")
    # Closure certifies that the connected transport classes are exactly orbits.
    for code, root in owners.items():
        for generator in range(9):
            check(owners[transform(code, generator)] == root, "orbit not closed")
    return roots, Counter(owners.values())


def outer_bits(a, b):
    rows = [(a // (2**i)) % 2 for i in range(3)]
    columns = [(b // (2**i)) % 2 for i in range(3)]
    value = 0
    for i in range(3):
        for j in range(3):
            if rows[i] and columns[j]:
                value += 2**(3 * i + j)
    return value


def check_potential(record, ranks, functions, decoder):
    cap = record["rank_cap"]
    check(type(cap) is int and cap in (15, 32), "unexpected cap")
    generators = [(outer_bits(a, b), ranks[a - 1][b - 1])
                  for a in range(1, 8) for b in range(1, 8)
                  if ranks[a - 1][b - 1] <= cap]
    reachable = {0}
    for bits, _ in generators:
        reachable |= {state ^ bits for state in tuple(reachable)}
    potential = record["potential"]
    check(len(potential) == 512 and potential[0] == 0, "bad potential origin/length")
    for state in range(512):
        if state not in reachable:
            check(potential[state] is None, "false reachability")
            continue
        check(type(potential[state]) is int and potential[state] >= 0, "bad potential value")
        for bits, cost in generators:
            other = potential[state ^ bits]
            check(type(other) is int and abs(other - potential[state]) <= cost,
                  "edge potential inequality fails")
    target = 2**0 + 2**4
    check(record["minimum"] == potential[target], "target potential mismatch")
    if target not in reachable:
        check(record["word"] == [], "false unreachable target")
        return
    # Check the attaining decoder literally on all 1024 port pairs.
    word = record["word"]
    total = 0
    for a, b in word:
        check(type(a) is int and type(b) is int and 1 <= a < 8 and 1 <= b < 8,
              "invalid factor in witness")
        check(ranks[a - 1][b - 1] <= cap, "witness exceeds cap")
        total += ranks[a - 1][b - 1]
    check(total == record["minimum"], "witness price mismatch")
    for x in range(32):
        for y in range(32):
            value = sum(functions[a][x] * functions[b][y] for a, b in word) % 2
            check(value == decoder[x][y], "witness fails all-pairs decoder identity")


def verify_data(certificate):
    check(certificate["schema"] == "five-cube-quadratic-code-v1", "wrong schema")
    check(certificate["basis"] == ["even", "odd", "h"], "wrong code basis")
    check(certificate["quotient_monomials"] == [list(m) for m in MONOMIAL_ORDER],
          "wrong polynomial order")
    check(certificate["target_coefficient_matrix_bits"] == 17, "wrong matrix target")
    check(certificate["transport_columns"] == ["child", "parent", "generator", "representative"],
          "wrong transport schema")
    orientations, gram, parity, decoder = geometry()
    masks = masks_for_domain(orientations, parity)
    check_isometries(orientations, gram, decoder)
    roots, sizes = check_transports(certificate)
    check(len(certificate["orbits"]) == 64, "wrong number of orbit records")
    check({r["representative"] for r in certificate["orbits"]} == roots,
          "orbit roots do not match transported coverage")
    rank_checks, capped_histogram = 0, Counter()
    for record in certificate["orbits"]:
        code = record["representative"]
        mask = masks[code]
        check(record["mask"] == mask and record["orbit_size"] == sizes[code],
              "wrong mask or orbit size")
        nonlinear = any(len(m) == 2 for m in polynomial(code))
        check(record["nonlinear"] is nonlinear, "wrong nonlinear classification")
        basis = [[1 - p for p in parity], parity, [(mask // (2**x)) % 2 for x in range(32)]]
        functions = [[sum(basis[i][x] for i in range(3) if a & (2**i)) % 2
                      for x in range(32)] for a in range(8)]
        check(len({tuple(f) for f in functions}) == 8, "evaluation basis is not independent")
        ranks = []
        for a in range(1, 8):
            row = []
            for b in range(1, 8):
                matrix = [[gram[x][y] for y in range(32) if functions[b][y]]
                          for x in range(32) if functions[a][x]]
                row.append(exact_rank(matrix))
                rank_checks += 1
            ranks.append(row)
        check(record["ranks"] == ranks, "rational rank table mismatch")
        check(record["unrestricted"]["rank_cap"] == 32 and record["rank15"]["rank_cap"] == 15,
              "wrong record cap")
        check_potential(record["unrestricted"], ranks, functions, decoder)
        check_potential(record["rank15"], ranks, functions, decoder)
        check(record["unrestricted"]["minimum"] == 32, "copy floor not established")
        minimum = record["rank15"]["minimum"]
        check(not nonlinear or minimum is None or minimum >= 34, "nonlinear gap not established")
        capped_histogram["unreachable" if minimum is None else str(minimum)] += sizes[code]
    expected_summary = {
        "quadratic_quotient_codes": 16383, "nonlinear_codes": 16368,
        "orbit_count": 64, "nonlinear_orbits": 62,
        "ordered_term_ranks": rank_checks, "coefficient_states_per_code": 512,
        "unrestricted_transition_checks": 64 * 512 * 49,
        "minimum_copy_rank_sum": 32,
        "nonlinear_minimum_with_rank_cap15": 34,
        "rank15_minimum_histogram_weighted_by_codes": dict(sorted(capped_histogram.items())),
        "finite_rank34_attaining_codes": capped_histogram["34"], "no_new_kappa": True,
    }
    check(certificate["summary"] == expected_summary, "summary/coverage mismatch")
    check(capped_histogram["34"] == 60, "sharp nonlinear rank-15 witness missing")
    return expected_summary


def check_source_files(certificate):
    manifest_bytes = (DIRECTORY / "SOURCES.json").read_bytes()
    check(hashlib.sha256(manifest_bytes).hexdigest() == certificate["source_manifest_sha256"],
          "source manifest binding differs")
    for record in json.loads(manifest_bytes)["retained_files"]:
        path = (DIRECTORY / record["local_path"]).resolve()
        check(DIRECTORY in path.parents, "source outside package")
        data = path.read_bytes()
        check(hashlib.sha256(data).hexdigest() == record["sha256"], "source content differs")
        blob = ("blob " + str(len(data)) + "\0").encode() + data
        check(hashlib.sha1(blob).hexdigest() == record["git_blob_sha1"], "source blob differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DIRECTORY / "CERTIFICATE.json")
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text())
    check_source_files(certificate)
    verify_data(certificate)
    print("PASS_INDEPENDENT_QUADRATIC_CODES polynomials=65536 transports=16383 "
          "rational_ranks=3136 all_pairs_witnesses=PASS no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print("FAIL_INDEPENDENT_QUADRATIC_CODES: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
