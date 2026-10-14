#!/usr/bin/env python3
"""Exact evidence for the global proper-star puncture theorem; standard library.

Copyright 2026 Luke Mansoor. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. Finite replay is not a
formal proof of the general theorem or of integer multiplication.
"""
import argparse
from hashlib import sha256
import importlib.util
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 43


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ports(p, k):
    return [sum(1 << (2 * q + s) for q, s in zip(qs, signs))
            for qs in combinations(range(p), k)
            for signs in product((0, 1), repeat=k)]


def generator(p, k):
    family = ports(p, k)
    stars = [s for degree in range(k) for s in ports(p, degree)]
    rows = [sum(1 << i for i, source in enumerate(family)
                if source & star == star) for star in stars]
    return family, stars, rows


def echelon(rows):
    basis = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return basis


def reduce(row, basis):
    for pivot in sorted(basis, reverse=True):
        if row >> pivot & 1:
            row ^= basis[pivot]
    return row


def syndrome(row, columns):
    value = 0
    while row:
        bit = row & -row
        value ^= columns[bit.bit_length() - 1]
        row ^= bit
    return value


def coordinates(port):
    return [i for i in range(port.bit_length()) if port >> i & 1]


def cube(slots, p, k):
    require(len(slots) == k and all(len(set(s)) == 2 for s in slots),
            "cube needs k slots with two distinct alternatives")
    used = set()
    for a, b in slots:
        require(0 <= a < 2 * p and 0 <= b < 2 * p, "cube coordinate range")
        pairs = {a // 2, b // 2}
        require(not used & pairs, "cube slots share a physical pair")
        used |= pairs
    vertices = [sum(1 << c for c in chosen) for chosen in product(*slots)]
    require(len(set(vertices)) == 1 << k, "cube vertices repeat")
    require(all(v.bit_count() == k and len({c // 2 for c in coordinates(v)}) == k
                for v in vertices), "cube contains an invalid port")
    return vertices


def generalized_face_checks(p, k, family, stars, rows, target):
    qs = sorted(c // 2 for c in coordinates(target))
    outside = [q for q in range(p) if q not in qs]
    lookup = {port: i for i, port in enumerate(family)}
    ordinary = set(cube([(2*q, 2*q+1) for q in qs], p, k))
    count = 0
    for codimension in range(min(len(outside), k) + 1):
        for fixed in combinations(range(k), codimension):
            for signs in product((0, 1), repeat=codimension):
                assignment = dict(zip(fixed, signs))
                slots = [(2*q, 2*q+1) for q in qs]
                for position, slot in enumerate(fixed):
                    slots[slot] = (2*qs[slot] + assignment[slot],
                                   2*outside[position] + (SEED + position) % 2)
                vertices = cube(slots, p, k)
                face = {v for v in ordinary
                        if all(v >> (2*qs[i] + sign) & 1
                               for i, sign in assignment.items())}
                require(set(vertices) & ordinary == face, "generalized cube face intersection")
                mask = sum(1 << lookup[v] for v in vertices)
                require(all((mask & row).bit_count() % 2 == 0 for row in rows),
                        "proper star has odd generalized-cube parity")
                # Independent direct monomial count checks the packed predicate.
                require(all(sum(v & s == s for v in vertices) % 2 == 0 for s in stars),
                        "direct generalized-cube monomial count")
                count += 1
    return count


def finite_case(p, k):
    family, stars, rows = generator(p, k)
    n = len(family)
    basis = echelon(rows)
    labels = [reduce(1 << i, basis) for i in range(n)]
    require(all(syndrome(row, labels) == 0 for row in rows), "quotient fails to annihilate G")
    require(len(echelon(labels)) == n - len(basis), "quotient rank-nullity")
    require(all(row.bit_count() % 2 == 0 for row in rows), "odd proper-star weight")
    require(all(labels) and len(set(labels)) == n, "zero or repeated syndrome column")
    pair_values = {labels[a] ^ labels[b] for a, b in combinations(range(n), 2)}
    if p == 6:
        require(len(pair_values) == comb(n, 2), "weight-four codeword exists")
    target_index = SEED % n
    target = family[target_index]
    jstar = sum(1 << c for c in coordinates(target)[:-1])
    witness = rows[stars.index(jstar)]
    support = [i for i in range(n) if witness >> i & 1]
    require(target_index in support, "attaining star misses target")
    require(len(support) == 2*(p-k+1), "sharp witness weight")
    require(syndrome(witness, labels) == 0, "attaining star fails dual")
    correction_count = 0
    for t in family:
        for overlap in range(1, k):
            exact = sum(1 << i for i, s in enumerate(family)
                        if (s & t).bit_count() == overlap)
            absorbed = 0
            for degree in range(overlap, k):
                if comb(degree, overlap) % 2:
                    for star in ports(p, degree):
                        if star & t == star:
                            absorbed ^= rows[stars.index(star)]
            require(exact == absorbed, "overlap correction absorption fails")
            require(syndrome(exact, labels) == 0, "correction not in star span")
            correction_count += 1
    controls = []
    for name, changed in [("single incidence flip", rows[0] ^ 1),
                           ("even-parity two-entry flip", rows[0] ^ 3),
                           ("forbidden degree-k singleton star", 1 << target_index)]:
        require(syndrome(changed, labels) != 0, "negative control accepted: " + name)
        controls.append(name)
    overlap_zero = sum(1 << i for i, s in enumerate(family) if not s & target)
    require(syndrome(overlap_zero, labels) != 0, "overlap-zero control accepted")
    controls.append("forbidden overlap-zero correction")
    damaged = labels[:]
    damaged[target_index] = 0
    require(any(syndrome(row, damaged) != 0 for row in rows), "damaged dual accepted")
    controls.append("zeroed dual column")
    slots = [(2*q, 2*q+1) for q in range(k)]
    slots[0] = (0, 2)
    try:
        cube(slots, p, k)
    except ValueError:
        controls.append("generalized cube reusing a physical pair")
    else:
        raise ValueError("invalid cube accepted")
    return dict(p=p, k=k, ports=n, stars_including_empty=len(stars),
                generator_rank=len(basis), dual_rank=n-len(basis),
                minimum_weight=len(support), minimum_one_target_deletions=len(support)-1,
                distinct_syndrome_columns=len(set(labels)),
                pair_count=comb(n, 2), distinct_pair_syndromes=len(pair_values),
                quotient_columns_hex=[hex(label) for label in labels],
                target_index=target_index, target=coordinates(target), star=coordinates(jstar),
                deleted_ports=[coordinates(family[i]) for i in support if i != target_index],
                correction_rows=correction_count,
                generalized_face_cubes=generalized_face_checks(p,k,family,stars,rows,target),
                negative_controls=controls)


def face_lemma_exhaustion():
    results = []
    for dimension in range(1, 5):
        n = 1 << dimension
        for budget in range(dimension + 1):
            faces = []
            for codimension in range(budget + 1):
                for fixed in combinations(range(dimension), codimension):
                    for values in product((0, 1), repeat=codimension):
                        faces.append(sum(1 << point for point in range(n)
                                         if all(point >> bit & 1 == value
                                                for bit, value in zip(fixed, values))))
            admitted = [s for s in range(1, 1 << n)
                        if all((s & f).bit_count() % 2 == 0 for f in faces)]
            minimum = min((s.bit_count() for s in admitted), default=None)
            require(minimum == (1 << (budget + 1) if budget < dimension else None),
                    "even-face lemma finite minimum differs")
            results.append(dict(dimension=dimension, codimension_budget=budget,
                                support_sets=(1 << n)-1, admitted_nonempty=len(admitted),
                                minimum_weight=minimum))
    return results


def span_exhaustion():
    results = []
    for p,k in [(2,2),(3,2),(4,2),(5,2),(6,2),(3,3),(4,4)]:
        family, _, rows = generator(p,k)
        basis = list(echelon(rows).values())
        span = [0]
        for row in basis:
            span += [value ^ row for value in span]
        minimum = min(value.bit_count() for value in span if value)
        require(minimum == 2*(p-k+1), "complete small-span distance mismatch")
        results.append(dict(p=p,k=k,ports=len(family),rank=len(basis),
                            codewords=len(span),minimum_weight=minimum))
    # At non-power-of-two k, the allowed corrections escape the star code:
    # target-local 1-stars plus overlap-1 isolate a target for k=3.
    family, stars, rows = generator(4,3)
    target = family[SEED % len(family)]
    coefficient = 0
    for coordinate in coordinates(target):
        coefficient ^= rows[stars.index(1 << coordinate)]
    coefficient ^= sum(1 << i for i,s in enumerate(family) if (s & target).bit_count() == 1)
    require(coefficient == 1 << family.index(target), "non-power-of-two positive control")
    require(reduce(coefficient, echelon(rows)) != 0, "power-of-two scope control failed")
    return results


def nonlocal_sharp_witness():
    family, stars, rows = generator(5,4)
    target_index = SEED
    target = family[target_index]
    sets = [(2,), (0,2), (2,4), (2,5), (2,6),
            (0,2,4), (0,2,5), (0,2,6), (2,4,6), (2,5,6)]
    coefficient = 0
    for subset in sets:
        coefficient ^= rows[stars.index(sum(1 << c for c in subset))]
    support = [i for i in range(len(family)) if coefficient >> i & 1]
    require(support == [0,2,42,43], "nonlocal sharp witness support differs")
    deleted = [0,2,42]
    live_mask = sum(1 << i for i in range(len(family)) if i not in deleted)
    require(coefficient & live_mask == 1 << target_index, "global punctured identity fails")
    local_rows = [row & live_mask for s,row in zip(stars,rows) if s and s & target == s]
    for j in (1,2,3):
        local_rows.append(sum(1 << i for i,s in enumerate(family)
                              if i not in deleted and (s & target).bit_count() == j))
    require(reduce(1 << target_index,echelon(local_rows)) != 0,
            "target-local cell criterion unexpectedly survives off-target witness")
    intersections = {s & target for s in family}
    surviving = {s & target for i,s in enumerate(family) if i not in deleted}
    require(intersections == surviving, "nonlocal example empties an intersection cell")
    return dict(p=5,k=4,target_index=target_index,target=coordinates(target),
                stars=[list(s) for s in sets], support_indices=support,
                deleted_indices=deleted, deleted_ports=[coordinates(family[i]) for i in deleted],
                all_intersection_cells_survive=True, global_decoder_passes=True,
                target_local_decoder_infeasible=True,
                control="The minimum threshold extends globally; the local cell criterion does not")


def verify():
    spec = importlib.util.spec_from_file_location("independent_global_star", HERE / "independent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = [finite_case(p,4) for p in (5,6)]
    independent = [module.verify(p) for p in (5,6)]
    for a,b in zip(cases,independent):
        for left,right in [("ports","ports"),("generator_rank","generator_rank"),
                           ("dual_rank","check_rank"),("minimum_weight","minimum_nonzero_weight"),
                           ("distinct_pair_syndromes","distinct_pair_syndromes"),
                           ("correction_rows","overlap_rows_checked")]:
            require(a[left] == b[right], "independent implementations disagree: " + left)
    return dict(status="PASS", assignment_seed=SEED,
                scope="Exact finite evidence for README's written general proof; no new kappa",
                bitset_quotient=cases, list_rref_nullspace=independent,
                even_face_exhaustion=face_lemma_exhaustion(),
                complete_small_spans=span_exhaustion(),
                nonlocal_sharp_witness=nonlocal_sharp_witness(),
                non_power_of_two_escape_control="PASS")


def verify_provenance():
    source = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    require(source["base_commit"] == "66849e1475c930fd7732b1a0067ffee7e1e95f60",
            "unexpected provenance base")
    require(source["selected_kappa"] == "51110230636731/31250000000000000",
            "unexpected selected context")
    root = HERE.parents[1]
    for item in source["context"]:
        path = (root / item["path"]).resolve()
        require(path.is_relative_to(root.resolve()), "context pin escapes repository")
        require(sha256(path.read_bytes()).hexdigest() == item["sha256"],
                "pinned context bytes changed: " + item["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a recomputed receipt after all checks")
    args = parser.parse_args()
    verify_provenance()
    result = verify()
    expected_path = HERE / "RESULTS.json"
    if expected_path.exists():
        require(result == json.loads(expected_path.read_text(encoding="utf-8")),
                "committed receipt differs from recomputed evidence")
    else:
        require(args.write is not None, "missing committed receipt")
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_GLOBAL_STAR_PUNCTURE: sharp deletion thresholds 3/5; "
          "2 independent F2 engines; 960 correction rows; 12 negative controls")


if __name__ == "__main__":
    main()
