#!/usr/bin/env python3
"""Exact, standard-library checks for the scoped restored-shear interfaces.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
No imports from any supplier or predecessor checker; no network or subprocesses.
The universal arguments are in PROOF.md, not inferred from these finite tests.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from math import gcd
from pathlib import Path
import runpy
import sys


HERE = Path(__file__).resolve().parent


class CheckError(Exception):
    pass


def require(condition, message):
    # Deliberately independent of Python's assert / optimization flag.
    if not condition:
        raise CheckError(message)


def ident(n):
    return tuple(1 << i for i in range(n))


def mxor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mmul(a, b):
    out = []
    for row in a:
        value = 0
        for j, other in enumerate(b):
            if (row >> j) & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def rank(a):
    pivots = {}
    for row in a:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def outer(u, v, n):
    return tuple(v if (u >> i) & 1 else 0 for i in range(n))


def pmul(a, b):
    """Matrix Laurent polynomials over F2, as exponent -> bit-row matrix."""
    n = len(next(iter(a.values())))
    zero = (0,) * n
    result = {}
    for e, x in a.items():
        for f, y in b.items():
            result[e + f] = mxor(result.get(e + f, zero), mmul(x, y))
    return {e: x for e, x in result.items() if any(x)}


def query_matrix(p, sign):
    return {0: mxor(ident(len(p)), p), sign: p}


def cyclic_reduce(polynomial, modulus):
    zero = (0,) * len(next(iter(polynomial.values())))
    result = {}
    for exponent, coefficient in polynomial.items():
        residue = exponent % modulus
        result[residue] = mxor(result.get(residue, zero), coefficient)
    return {e: x for e, x in result.items() if any(x)}


def projector_catalogue(n):
    # Enumerate *all* binary matrices, independently of the rank-one formula.
    mask = (1 << n) - 1
    actual = set()
    for bits in range(1 << (n * n)):
        rows = tuple((bits >> (n * i)) & mask for i in range(n))
        if rank(rows) == 1 and mmul(rows, rows) == rows:
            actual.add(rows)
    factored = {
        outer(u, v, n)
        for u in range(1, 1 << n)
        for v in range(1, 1 << n)
        if (u & v).bit_count() % 2
    }
    require(actual == factored, "independent projector catalogues disagree")
    return sorted(actual)


def algebra_checks():
    reports = []
    for n in (2, 3, 4):
        eye, zero = ident(n), (0,) * n
        projectors = projector_catalogue(n)
        nilpotents = {
            outer(u, v, n)
            for u in range(1, 1 << n)
            for v in range(1, 1 << n)
            if not (u & v).bit_count() % 2
        }
        targets = {p: {0: mxor(eye, p), 1: p} for p in nilpotents}
        counts = Counter()
        by_sign = Counter()
        fixed = outer(1, 2, n)
        fixed_private = 0
        checked = 0
        for p, q, left, right in product(projectors, projectors, (-1, 1), (-1, 1)):
            actual = pmul(query_matrix(p, left), query_matrix(q, right))
            coefficient = actual.get(1, zero)
            is_shear = coefficient in targets and actual == targets[coefficient]
            pq = mmul(p, q)
            predicted = (
                p != q and left == -right
                and ((left == 1 and pq == q) or (left == -1 and pq == p))
            )
            require(is_shear == predicted, "two-query classification counterexample")
            if is_shear:
                require(coefficient == mxor(p, q), "wrong shear coefficient")
                counts[coefficient] += 1
                by_sign[f"{left},{right}"] += 1
                if n >= 3 and coefficient == fixed:
                    fixed_private += bool((p[2] & 4) and (q[2] & 4))
            checked += 1
        require(set(counts) == nilpotents, "missing nilpotent target")
        require(set(counts.values()) == {1 << n}, "wrong factorizations per target")
        require(fixed_private == 0, "private-diagonal restriction failed")
        for p, sign in product(projectors, (-1, 1)):
            require(query_matrix(p, sign) not in targets.values(), "one query gives a shear")
        reports.append({
            "rows": n, "projectors": len(projectors), "ordered_signed_pairs": checked,
            "nonzero_rank_one_nilpotent_targets": len(nilpotents),
            "solutions": sum(counts.values()), "solutions_per_target": 1 << n,
            "solutions_by_left_right_sign": dict(sorted(by_sign.items())),
            "fixed_data_shear_solutions_with_both_private_diagonals_one": fixed_private,
        })

    # Exhaust the *fixed* four native charts on (target, source, private).
    # Stop at depth four, after completing the entire layer (not first success).
    n, eye = 3, ident(3)
    target = {0: mxor(eye, outer(1, 2, n)), 1: outer(1, 2, n)}
    alphabet = [(a, b, s) for a, b, s in product((0, 1), (0, 1), (-1, 1))]
    layers = []
    for length in range(5):
        successes = 0
        for word in product(alphabet, repeat=length):
            value = {0: eye}
            for a, b, sign in word:
                p = outer(4 | a, 4 | (b << 1), n)
                value = pmul(query_matrix(p, sign), value)
            successes += value == target
        layers.append({"queries": length, "words": 8 ** length, "solutions": successes})
    require([x["solutions"] for x in layers] == [0, 0, 0, 0, 24], "native chart count")
    return {"projector_pairs": reports, "native_chart_layers": layers}


def inverse_address(word):
    result = []
    for event in reversed(word):
        if event["op"] == "child":
            result.append(deepcopy(event))
        else:
            diagonal = F(event["diagonal"])
            result.append({
                "op": "affine", "dst": event["dst"], "diagonal": str(1 / diagonal),
                "terms": [[i, str(-F(c) / diagonal)] for i, c in event["terms"]],
            })
    return result


def specialize(q, modulus):
    q = F(q)
    if modulus is None:
        return q
    return q.numerator * pow(q.denominator, -1, modulus) % modulus


def address_apply(word, address, modulus=None):
    z = list(address)
    for event in word:
        if event["op"] == "child":
            i, j = event["fields"]
            z[i], z[j] = z[j], z[i]
        elif event["op"] == "affine":
            i = event["dst"]
            z[i] = specialize(event["diagonal"], modulus) * z[i] + sum(
                specialize(c, modulus) * z[j] for j, c in event["terms"]
            )
            if modulus is not None:
                z[i] %= modulus
        else:
            raise CheckError("unknown ADDRESS operation")
    return tuple(z)


S = (1, 0, 1, -1, 0, -1)
R = (1, 0, -1, -1, 0, 1)


def closed_address(address, sign, modulus=None):
    amount = sum(r * x for r, x in zip(R, address)) * specialize(F(sign, 4), modulus)
    z = [x + s * amount for x, s in zip(address[:6], S)] + list(address[6:])
    return tuple(x % modulus for x in z) if modulus else tuple(z)


def orbit(modulus, scale=1):
    return [tuple(((scale if i == 0 else 0) + specialize(F(k * scale, 4), modulus) * S[i]) % modulus
                  for i in range(6)) for k in range(modulus // gcd(scale, modulus))]


def permutations(word, points, modulus):
    lookup = {p: i for i, p in enumerate(points)}
    require(len(lookup) == len(points), "orbit addresses repeat")
    result = {}
    for sign, w in ((1, word), (-1, inverse_address(word))):
        push = [lookup[address_apply(w, p, modulus)] for p in points]
        require(sorted(push) == list(range(len(points))), "ADDRESS map is not a permutation")
        result[sign] = push
    return result


def address_checks(packet):
    word = packet["address_forward"]
    require(Counter(e["op"] for e in word) == {"affine": 6, "child": 1}, "ADDRESS invoice")
    for e in word:
        if e["op"] == "affine":
            require(all(0 <= i < e["dst"] < 6 for i, _ in e["terms"]), "unordered affine read")
            diagonal = F(e["diagonal"])
            for v in (abs(diagonal.numerator), diagonal.denominator):
                require(v > 0 and v & (v - 1) == 0, "diagonal excludes an odd prime")
            for _, c in e["terms"]:
                d = F(c).denominator
                require(d & (d - 1) == 0, "coefficient excludes an odd prime")
        else:
            require(e["fields"] == [0, 5], "wrong recursive fields")
    columns = 0
    moduli = (None, 3, 9, 27, 11, 121)
    for m, sign, j in product(moduli, (-1, 1), range(8)):
        column = tuple(int(i == j) for i in range(8))
        w = word if sign == 1 else inverse_address(word)
        actual = address_apply(w, column, m)
        require(actual == closed_address(column, sign, m), "rational/modular ADDRESS identity")
        require(address_apply(inverse_address(w), actual, m) == column, "ADDRESS inverse")
        columns += 1
    orbit_reports = []
    for m, scale in ((3, 1), (9, 1), (27, 1), (11, 1), (121, 1), (9, 3), (27, 3), (121, 11)):
        points = orbit(m, scale)
        maps = permutations(word, points, m)
        size = len(points)
        require(maps[1] == [(k + 1) % size for k in range(size)], "forward orientation")
        require(maps[-1] == [(k - 1) % size for k in range(size)], "inverse orientation")
        orbit_reports.append({"modulus": m, "initial_scale": scale, "length": size})
    return {"basis_columns_including_two_address_spectators": columns,
            "rational_and_modular_domains": ["Q", 3, 9, 27, 11, 121], "orbits": orbit_reports}


def bit_apply(program, state, maps):
    rows = [list(x) for x in state]
    for e in program:
        if e["op"] == "xor":
            d, s = e["dst"], e["src"]
            rows[d] = [a ^ b for a, b in zip(rows[d], rows[s])]
        elif e["op"] == "copy":
            rows[e["dst"]] = list(rows[e["src"]])
        elif e["op"] == "query":
            row = e["row"]
            out = [0] * len(rows[row])
            for old, new in enumerate(maps[e["direction"]]):
                out[new] = rows[row][old]
            rows[row] = out
        elif e["op"] == "clear":
            rows[e["row"]] = [0] * len(rows[e["row"]])
        else:
            raise CheckError("unknown BIT operation")
    return rows


def target_bit(state, clean=False):
    # Independent expected endpoint: closed orbit shift, not the emitted maps.
    out = [list(x) for x in state]
    source = state[1]
    out[0] = [x ^ y ^ source[(i - 1) % len(source)]
              for i, (x, y) in enumerate(zip(state[0], source))]
    if clean:
        out[3] = [0] * len(source)
    return out


def bit_identity(size):
    # Each integer bit is a different input basis column. XOR transports all
    # dirty columns simultaneously; there is no randomized VALUE sampling.
    return [[1 << (r * size + k) for k in range(size)] for r in range(4)]


def invoice(program):
    counts = Counter(e["op"] for e in program)
    return {"ordinary_children": counts["query"], "ordered_affine_events": 6 * counts["query"],
            "xor_scans": counts["xor"], "copy_scans": counts["copy"], "clear_scans": counts["clear"]}


def endpoint_checks(packet):
    word, programs = packet["address_forward"], packet["programs"]
    coverage = []
    for m, scale in ((3, 1), (9, 1), (27, 1), (11, 1), (121, 1), (9, 3), (27, 3), (121, 11)):
        points = orbit(m, scale)
        maps = permutations(word, points, m)
        state = bit_identity(len(points))
        for name, program in programs.items():
            clean = name == "clean_private"
            actual = bit_apply(program, state, maps)
            require(actual == target_bit(state, clean), f"{name}: dirty endpoint failure")
            twice = bit_apply(program, actual, maps)
            expected = [list(x) for x in state]
            if clean:
                expected[3] = [0] * len(points)
            require(twice == expected, f"{name}: completed DATA inverse failure")
        coverage.append({"modulus": m, "initial_scale": scale, "dirty_basis_columns": 4 * len(points)})
    # Every assignment at an address fixed by h. No hidden nontrivial-orbit assumption.
    fixed_checks = 0
    fixed_maps = {1: [0], -1: [0]}
    fixed_address = (0, 1, 0, 0, 1, 0)
    require(address_apply(word, fixed_address, 9) == fixed_address, "fixed address")
    for bits, (name, program) in product(product((0, 1), repeat=4), programs.items()):
        state = [[b] for b in bits]
        expected = deepcopy(state)
        if name == "clean_private":
            expected[3] = [0]
        require(bit_apply(program, state, fixed_maps) == expected, "fixed point VALUE failure")
        fixed_checks += 1
    expected_invoices = {
        "no_private": {"ordinary_children": 2, "ordered_affine_events": 12, "xor_scans": 2, "copy_scans": 0, "clear_scans": 0},
        "dirty_private": {"ordinary_children": 4, "ordered_affine_events": 24, "xor_scans": 5, "copy_scans": 0, "clear_scans": 0},
        "clean_private": {"ordinary_children": 1, "ordered_affine_events": 6, "xor_scans": 2, "copy_scans": 1, "clear_scans": 1},
    }
    invoices = {name: invoice(p) for name, p in programs.items()}
    require(invoices == expected_invoices, "paid-event census changed")
    require(all(e.get("row") != 3 and e.get("dst") != 3 and e.get("src") != 3
                for e in programs["no_private"]), "private row used in no-private program")
    for e in programs["dirty_private"]:
        require((e["op"] == "query" and e["row"] == 3)
                or (e["op"] == "xor" and (e["dst"], e["src"]) in {(3, 1), (0, 3), (0, 1)}),
                "dirty-private program left the triangular query model")
    return {"orbits": coverage, "basis_columns_per_program": sum(c["dirty_basis_columns"] for c in coverage),
            "fixed_point_assignments_across_three_programs": fixed_checks, "invoices": invoices,
            "clean_private_contract": "private input may be discarded; DATA and spectator input columns preserved as specified"}


def negative_controls(packet):
    word, programs = packet["address_forward"], packet["programs"]
    maps = permutations(word, orbit(11), 11)
    state = bit_identity(11)
    wanted = target_bit(state)
    rejected = []
    for name, original in programs.items():
        for i, e in enumerate(original):
            if e["op"] == "query":
                mutated = deepcopy(original)
                mutated.pop(i)
                require(bit_apply(mutated, state, maps) != target_bit(state, name == "clean_private"),
                        "omitted query accepted")
                rejected.append(f"{name}:omit_query_{i}")
    wrong = deepcopy(programs["no_private"])
    wrong[0]["direction"] = 1
    require(bit_apply(wrong, state, maps) != wanted, "wrong inverse accepted")
    rejected.append("no_private:use_forward_as_inverse")
    for i in (1, 3):
        wrong = deepcopy(programs["no_private"])
        wrong.pop(i)
        require(bit_apply(wrong, state, maps) != wanted, "missing XOR accepted")
        rejected.append(f"no_private:omit_xor_{i}")
    clean = bit_apply(programs["clean_private"], state, maps)
    require(clean != wanted, "owned scratch was accepted as restored arbitrary dirt")
    rejected.append("clean_private:claim_arbitrary_dirty_restoration")
    for i in (0, len(programs["clean_private"]) - 1):
        wrong = deepcopy(programs["clean_private"])
        wrong.pop(i)
        require(bit_apply(wrong, state, maps) != target_bit(state, True), "missing copy/clear accepted")
        rejected.append(f"clean_private:omit_{programs['clean_private'][i]['op']}_{i}")
    # Reproduce the distinction: the completed shear is self-inverse, but the
    # unfinished dirty module's inverse does not undo a subsequent wipe.
    dirty_module = [
        {"op": "xor", "dst": 3, "src": 1}, {"op": "xor", "dst": 0, "src": 3},
        {"op": "query", "row": 3, "direction": 1},
        {"op": "xor", "dst": 0, "src": 3}, {"op": "xor", "dst": 3, "src": 1},
    ]
    inverse_module = []
    for e in reversed(dirty_module):
        e = deepcopy(e)
        if e["op"] == "query":
            e["direction"] *= -1
        inverse_module.append(e)
    clean_start = deepcopy(state)
    clean_start[3] = [0] * 11
    forward = bit_apply(programs["clean_private"], clean_start, maps)
    require(bit_apply(inverse_module, forward, maps) != clean_start, "erasure is reversible on dirty module")
    rejected.append("clean_private:reuse_unfinished_module_inverse_after_clear")
    # A scalar endpoint match cannot justify omitting its recursive child.
    missing_child = [e for e in word if e["op"] != "child"]
    column = (1, 0, 0, 0, 0, 0)
    require(address_apply(missing_child, column) != closed_address(column, 1), "unpaid ADDRESS child accepted")
    rejected.append("address:omit_ordinary_child_keep_affine_wrappers")
    wrong = deepcopy(word)
    wrong[2]["terms"][0][1] = "1"
    require(address_apply(wrong, column) != closed_address(column, 1), "wrong ADDRESS coefficient accepted")
    rejected.append("address:change_5_over_4_to_1")
    # A concrete counterexample to extending the opposite-sign classification
    # to order two: two same-sign queries can give a shear when t^2=1.
    p, q, n = (1, 0), (3, 0), (2, 0)
    same_sign = pmul(query_matrix(p, 1), query_matrix(q, 1))
    target = {0: mxor(ident(2), n), 1: n}
    require(same_sign != target and cyclic_reduce(same_sign, 2) == cyclic_reduce(target, 2),
            "order-two counterexample failed")
    rejected.append("classification:extending_opposite_sign_rule_to_order_two")
    return {"rejected": rejected, "count": len(rejected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--write-results", action="store_true", help="regenerate EXPECTED.json locally")
    parser.add_argument("-k", choices=("algebra", "address", "endpoints", "full_domain", "controls"), help="focused iteration")
    args = parser.parse_args()
    require(not (args.write_results and args.k), "partial results must not replace the complete receipt")
    packet = json.loads((HERE / "PROGRAM.json").read_text())
    require(packet["schema"] == "native-restored-shear-v1", "packet schema")
    require(packet["rows"] == ["target", "source", "spectator", "private"], "row labels")
    require(set(packet["programs"]) == {"no_private", "dirty_private", "clean_private"}, "program inventory")
    checks = {"algebra": lambda: algebra_checks(), "address": lambda: address_checks(packet),
              "endpoints": lambda: endpoint_checks(packet),
              "full_domain": lambda: runpy.run_path(str(HERE / "full_domain_check.py"))["check_full_domain"](packet),
              "controls": lambda: negative_controls(packet)}
    report = {name: f() for name, f in checks.items() if args.k is None or args.k == name}
    destination = HERE / "EXPECTED.json"
    if args.write_results:
        destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("WROTE EXPECTED.json (all five check groups)")
    else:
        expected = json.loads(destination.read_text())
        if args.k:
            expected = {args.k: expected[args.k]}
        require(report == expected, "computed evidence differs from EXPECTED.json")
        print("PASS_RESTORED_SHEAR_INTERFACES" + (f" [{args.k}]" if args.k else ""))
        if not args.k:
            pairs = sum(r["ordered_signed_pairs"] for r in report["algebra"]["projector_pairs"])
            words = sum(r["words"] for r in report["algebra"]["native_chart_layers"])
            print(f"{pairs} signed projector pairs; {words} native-chart words; "
                  f"{report['endpoints']['basis_columns_per_program']} BIT basis columns per program; "
                  f"{report['controls']['count']} negative controls")
            print("Independent full-domain replay: 729 addresses; 2916 basis columns per program; "
                  f"{report['full_domain']['endpoint_and_completed_inverse_cases']} endpoint/inverse cases")


if __name__ == "__main__":
    try:
        main()
    except (CheckError, KeyError, ValueError, TypeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
