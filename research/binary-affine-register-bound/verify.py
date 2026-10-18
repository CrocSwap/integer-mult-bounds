#!/usr/bin/env python3
"""Verify the binary-affine register bound. --full also runs complete native BFS.

Default/--quick: dimensions 1..3, all mathematical controls and larger fixtures.
--full: independent C++ BFS for every affine map through dimension 4, compared
pointwise with Python ranks and explicit attaining factorizations. Needs C++17.
Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, deque
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import algebra as A

INPUTS = {"research/bit-three-register-lower-bound/README.md",
          "research/r439-bsection-stars-seed01/README.md"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(rows):
        out = {}
        for k, v in rows:
            A.need(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    def bad(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=bad)


def source_check(root=ROOT, package=HERE):
    rows = [r for r in load(package / "SOURCES.json")["files"] if r["usage"] == "input"]
    A.need(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS, "source inventory")
    for row in rows:
        A.need(sha((root / row["path"]).read_bytes()) == row["sha256"], "source hash: " + row["path"])
    return {r["path"]: r["sha256"] for r in rows}


def census(n, distances=None):
    histogram, count = Counter(), 0
    digest = hashlib.sha256()
    units = set(A.group_units(n))
    rank_one = set()
    if distances is not None:
        A.need(len(distances) == 1 << (n * (n + 1)), "distance array length")
    for linear in A.linear_maps(n):
        for b in range(1 << n):
            g = A.affine(linear, b)
            factors = A.affine_factors(g)
            A.validate_factors(g, factors)
            rho = A.displacement(g)
            count += 1
            histogram[rho] += 1
            if rho == 1:
                rank_one.add(g)
            if distances is not None:
                A.need(distances[A.encode(g)] == rho, "Cayley distance disagrees with attaining rank")
            if n <= 3:
                for x in range(1 << n):
                    y = x
                    for t in reversed(factors):
                        y = A.apply(t, y | (1 << n))
                    A.need(y == A.apply(g, x | (1 << n)), "literal affine-point endpoint")
            digest.update(struct.pack("<IB", A.encode(g), len(factors)))
            for t in factors:
                digest.update(struct.pack("<I", A.encode(t)))
    expected_order = (1 << n)
    for i in range(n):
        expected_order *= (1 << n) - (1 << i)
    A.need(count == expected_order, "complete affine order")
    A.need(rank_one == units, "complete paid alphabet")
    if distances is not None:
        A.need(sum(v != 255 for v in distances) == count, "native reachable set")
    return dict(dimension=n, states=count, generators=len(units),
                histogram=[histogram[i] for i in range(n + 1)],
                factorization_sha256=digest.hexdigest())


def priced(nmat, g):
    r, d = len(nmat), len(g)
    A.need(A.rank(nmat) == 1 and A.mul(nmat, nmat) == nmat, "rank-one idempotent")
    A.need(A.rank(tuple(row & ((1 << d) - 1) for row in g)) == d,
           "invertible address map")
    A.need(A.displacement(g) == 1, "rank-one address displacement")
    image = A.representation(nmat, g)
    A.need(A.rank(tuple(row ^ (1 << i) for i, row in enumerate(image))) == 1,
           "one-call representation rank")
    return image


def independent_point_bfs(n):
    # Tuple permutations of actual affine points, rather than homogeneous matrices.
    identity = tuple(range(1 << n))
    generators = [tuple(A.apply(g, x | (1 << n)) for x in identity) for g in A.group_units(n)]
    distance, queue = {identity: 0}, deque([identity])
    while queue:
        p = queue.popleft()
        for g in generators:
            q = tuple(g[p[x]] for x in identity)
            if q not in distance:
                distance[q] = distance[p] + 1
                queue.append(q)
    for a in A.linear_maps(n):
        for b in range(1 << n):
            g = A.affine(a, b)
            permutation = tuple(A.apply(g, x | (1 << n)) for x in identity)
            A.need(distance[permutation] == A.displacement(g), "point-permutation BFS")
    return len(distance)


def controls():
    checked = []
    # Ignoring the affine column underprices every nonzero translation.
    translation = (3,)
    A.need(A.rank(((translation[0] & 1) ^ 1,)) == 0 and A.displacement(translation) == 1,
           "translation rank witness")
    checked.append("linear_part_alone_misses_translation")
    # Reversing noncommuting address factors changes the formal endpoint.
    g, h = (3, 2), (1, 6)
    A.need(A.amul(g, h) != A.amul(h, g), "noncommuting affine witness")
    p = A.ring_mul(A.ring_call((1,), g), A.ring_call((1,), h))
    q = A.ring_mul(A.ring_call((1,), h), A.ring_call((1,), g))
    A.need(p != q and p == [[{A.amul(g, h)}]], "group product order")
    checked.append("noncommuting_order_is_material")
    # Correct on a clean helper, incorrect on arbitrary dirty helper input.
    leaky = A.ring_call((3, 0), translation)
    target = [[{translation}, set()], [set(), {A.eye(1)}]]
    A.need([row[0] for row in leaky] == [row[0] for row in target] and leaky != target,
           "dirty-helper target leakage")
    A.need(leaky[0][1] == {A.eye(1), translation}, "explicit dirty discrepancy")
    checked.append("clean_only_endpoint_is_insufficient")
    # The natural representation and augmentation together are not a faithful
    # group-algebra identity oracle. Use exact coefficients for upper bounds.
    group = {A.affine(a, b) for a in A.linear_maps(2) for b in range(4)}
    A.need(len(group) == 24 and group and A.ring_image([[group]], 2) == (0, 0, 0),
           "nonzero group-algebra kernel witness")
    checked.append("natural_representation_zero_is_not_formal_zero")
    for nmat, address, message in [((1,), A.amul(g, h), "rank-two-address"),
                                   (A.eye(2), translation, "rank-two-scalar")]:
        try:
            priced(nmat, address)
        except ValueError:
            pass
        else:
            raise ValueError(message + " accepted as one unit")
        image = A.representation(nmat, address)
        A.need(A.rank(tuple(row ^ (1 << i) for i, row in enumerate(image))) == 2,
               "underpriced rank-two witness")
        checked.append(message)
    # A free register XOR is not an admissible diagonal group target: its
    # augmentation is nonidentity. Free address maps would also invalidate
    # the model's cost: translation above would then cost zero instead of one.
    xor = (3, 2)
    A.need(A.rank(tuple(row ^ (1 << i) for i, row in enumerate(xor))) == 1,
           "unremoved free scalar baseline")
    checked.append("free_scalar_baseline_must_cancel_by_augmentation")
    return checked


def register_checks():
    count = 0
    for r in range(1, 5):
        for nmat in A.projectors(r):
            for d in range(1, 5):
                for g in A.group_units(d):
                    priced(nmat, g)
                    count += 1
    rng = random.Random(2601)
    words, prefixes, identities = 0, 0, 0
    for r in (2, 3, 4):
        projectors = list(A.projectors(r))
        units = list(A.group_units(2))
        for _ in range(32):
            ring, image = A.ring_eye(r, 2), A.eye(3 * r)
            for length in range(1, 7):
                nmat, g = rng.choice(projectors), rng.choice(units)
                ring = A.ring_mul(ring, A.ring_call(nmat, g))
                image = A.mul(image, priced(nmat, g))
                A.need(A.ring_image(ring, 2) == image, "formal-to-natural representation homomorphism")
                A.need(A.rank(tuple(row ^ (1 << i) for i, row in enumerate(image))) <= length,
                       "paid-prefix rank budget")
                prefixes += 1
            words += 1
    # Exact formal attaining targets, including a restored fourth dirty register.
    targets = [(3, 2), (1, 6), A.amul((3, 2), (1, 6))]
    ring = A.ring_eye(4, 2)
    bill = 0
    for j, target in enumerate(targets):
        projector = tuple(1 << j if i == j else 0 for i in range(4))
        for t in A.affine_factors(target):
            ring = A.ring_mul(ring, A.ring_call(projector, t))
            bill += 1
    expected = [[{targets[i] if i < 3 else A.eye(2)} if i == j else set()
                 for j in range(4)] for i in range(4)]
    A.need(ring == expected and bill == 4, "four-register formal attaining word")
    identities += 1
    A.need(A.ring_call((1,), A.eye(2)) == A.ring_eye(1, 2), "identity group coefficient cancellation")
    # Three mutually noncommuting affine targets, each of displacement rank3.
    # The fourth register can be arbitrary and is returned identically.
    large_targets = [A.affine((4, 5, 2), b) for b in (0, 1, 3)]
    A.need(all(A.displacement(g) == 3 for g in large_targets), "three full-rank targets")
    A.need(all(A.amul(g, h) != A.amul(h, g) for i, g in enumerate(large_targets)
               for h in large_targets[i + 1:]), "noncommuting target triple")
    calls = []
    for j, target in enumerate(large_targets):
        nmat = tuple(1 << j if i == j else 0 for i in range(4))
        calls.extend((nmat, t) for t in A.affine_factors(target))
    wanted = [[{large_targets[i] if i < 3 else A.eye(3)} if i == j else set()
               for j in range(4)] for i in range(4)]
    def replay(word):
        result = A.ring_eye(4, 3)
        for nmat, t in word:
            result = A.ring_mul(result, A.ring_call(nmat, t))
        return result
    A.need(len(calls) == 9 and replay(calls) == wanted, "nine-call formal attaining word")
    A.need(replay(calls[:4] + calls[5:]) != wanted, "omitted paid call must fail")
    identities += 1
    # Scalar basis conjugation: B E B^-1, with every GL(2,2) basis and paid label.
    for b in A.linear_maps(2):
        inv = next(c for c in A.linear_maps(2) if A.mul(b, c) == A.eye(2))
        def lift(x):
            return [[{A.eye(2)} if x[i] >> j & 1 else set() for j in range(2)] for i in range(2)]
        for g in A.group_units(2):
            nmat = A.mul(A.mul(b, (1, 0)), inv)
            explicit = A.ring_mul(A.ring_mul(lift(b), A.ring_call((1, 0), g)), lift(inv))
            A.need(explicit == A.ring_call(nmat, g), "free scalar normalization")
            identities += 1
    return dict(elementary_rank_checks=count, words=words, prefixes=prefixes,
                exact_formal_identities=identities, four_register_attaining_cost=bill,
                noncommuting_three_target_cost=len(calls), omitted_paid_call_rejected=True,
                noncommuting_target_codes=[A.encode(g) for g in large_targets])


def larger_fixtures():
    rng = random.Random(2602)
    total = 0
    for d in (5, 8, 16, 32):
        for _ in range(8):
            linear = list(A.eye(d))
            for _ in range(4 * d):
                i, j = rng.sample(range(d), 2)
                linear[i] ^= linear[j]
            g = A.affine(tuple(linear), rng.randrange(1 << d))
            A.validate_factors(g, A.affine_factors(g))
            total += 1
    return total


def quick():
    return dict(censuses=[census(d) for d in range(1, 4)],
                point_bfs_states=[independent_point_bfs(d) for d in (1, 2)],
                controls=controls(), register_checks=register_checks(),
                larger_fixtures=larger_fixtures(), larger_dimensions=[5, 8, 16, 32])


def full(work):
    compiler = os.environ.get("CXX", "g++")
    binary = work / "cayley"
    build = subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                            str(HERE / "cayley.cpp"), "-o", str(binary)],
                           capture_output=True, text=True, timeout=120)
    A.need(build.returncode == 0, "native build: " + build.stdout + build.stderr)
    reports = []
    for d in range(1, 5):
        path = work / ("distance-" + str(d) + ".bin")
        proc = subprocess.run([str(binary), str(d), str(path)], capture_output=True, text=True, timeout=180)
        A.need(proc.returncode == 0, "native BFS: " + proc.stdout + proc.stderr)
        native = json.loads(proc.stdout)
        distance = path.read_bytes()
        exact = census(d, distance)
        wanted = {k: exact[k] for k in ["dimension", "generators", "states", "histogram"]}
        wanted["edges"] = exact["states"] * exact["generators"]
        A.need(canonical(native) == canonical(wanted), "native full coverage report")
        reports.append(dict(exact, edges=native["edges"], distance_sha256=sha(distance)))
    return reports


def check_expected(name, value, package=HERE):
    A.need(canonical(load(package / "EXPECTED.json")[name]) == canonical(value), "expected " + name + " certificate")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="explicit default; omits native dimension4 census")
    parser.add_argument("--full", action="store_true", help="also run complete independent native census")
    parser.add_argument("--work", type=Path, help="new output directory, only with --full")
    args = parser.parse_args()
    A.need(not (args.quick and args.full), "choose quick or full")
    A.need(args.full or args.work is None, "--work requires --full")
    pins = source_check()
    report = quick()
    check_expected("quick", report)
    print("PASS_BINARY_AFFINE_QUICK affine_maps=1370 controls=7 not_full_dimension4_census")
    if args.full:
        def execute(work):
            result = full(work)
            check_expected("full", result)
            A.need(source_check() == pins, "source changed during replay")
            receipt = dict(quick=report, full=result)
            (work / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
            print("PASS_BINARY_AFFINE_FULL affine_maps=" + str(sum(r["states"] for r in result)) +
                  " exact_distances_and_attaining_words=true")
            print("receipt_sha256=" + sha(canonical(receipt)))
        if args.work:
            A.need(not args.work.exists(), "output directory already exists")
            args.work.mkdir(parents=True)
            execute(args.work)
        else:
            with tempfile.TemporaryDirectory(prefix="binary-affine-full-") as path:
                execute(Path(path))
    A.need(source_check() == pins, "source changed during replay")


if __name__ == "__main__":
    main()
