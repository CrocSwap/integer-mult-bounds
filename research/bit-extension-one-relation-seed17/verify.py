#!/usr/bin/env python3
"""Exact finite evidence for PROOF.md; not an enumeration proof of its theorem.

Prepared for Charan (theon199) with substantial OpenAI Codex assistance.
Apache-2.0. No third-party implementation is imported.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ZERO = (0, 0, 0, 0)
ID = (1, 0, 0, 1)
# Integer exponents represent twice the actual rational address matrix.
FRAMES = ((2, 0, 0, 0), (0, 0, 0, 2),
          (1, 1, 1, 1), (1, -1, -1, 1))
OUTSIDE = (0, 2, 0, 0)
SHIFT = (2, 0, 0, 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class Field:
    def __init__(self, degree, polynomial):
        self.q = 1 << degree
        self.degree = degree
        self.polynomial = polynomial
        self.table = [[self._multiply(a, b) for b in range(self.q)]
                      for a in range(self.q)]
        for a in range(1, self.q):
            require(any(self.table[a][b] == 1 for b in range(1, self.q)),
                    "polynomial does not define a field")

    def _multiply(self, a, b):
        value = 0
        while b:
            if b & 1:
                value ^= a
            b >>= 1
            a <<= 1
            if a & self.q:
                a ^= self.polynomial
        return value

    def mm(self, a, b):
        f = self.table
        return tuple(f[a[2*i]][b[j]] ^ f[a[2*i+1]][b[2+j]]
                     for i in range(2) for j in range(2))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def expsum(a, b):
    return tuple(x+y for x, y in zip(a, b))


def scalar_census(field):
    """All q^4 matrices, independently of an outer-product parametrization."""
    classes = defaultdict(list)
    projectors = []
    f = field.table
    for n in product(range(field.q), repeat=4):
        a, b, c, d = n
        if n == ZERO or f[a][d] ^ f[b][c]:
            continue
        if field.mm(n, n) != n:
            continue
        require(a ^ d == 1, "rank-one idempotent trace")
        projectors.append(n)
        classes[(b, c)].append(n)
    expected = field.q * (field.q + 1)
    require(len(projectors) == expected, "projector inventory")
    cyclic = []
    for (b, c), ns in sorted(classes.items()):
        require(len(ns) == 2, "two roots for every realized pair")
        require(add(ns[0], ns[1]) == ID, "complementary pair")
        if b and c:
            cyclic.extend(ns)
            for n in ns:
                require(field.table[n[0]][n[0] ^ 1] == field.table[b][c],
                        "quadratic classification")
        else:
            require(all(n[0] in (0, 1) for n in ns), "triangular diagonal")
    data = {
        "q": field.q, "polynomial": field.polynomial,
        "matrices_examined": field.q**4,
        "projectors": len(projectors), "patterns": len(classes),
        "cyclic_patterns": len(cyclic)//2,
        "class_sizes": dict(sorted(Counter(map(len, classes.values())).items())),
        "projectors_sha256": digest(projectors),
    }
    if field.q == 4:
        data["projectors_binary_sha256"] = digest(sorted(binary_rows(field, n)
                                                         for n in projectors))
    return data, sorted(cyclic)


def word(field, gates):
    """Right-multiply exact sparse matrix polynomials, retaining all exponents."""
    state = {ZERO: ID}
    for frame, n in gates:
        output = {}
        for address, coefficient in state.items():
            for delta, matrix in ((ZERO, add(ID, n)), (frame, n)):
                address2 = expsum(address, delta)
                v = add(output.get(address2, ZERO), field.mm(coefficient, matrix))
                if v != ZERO:
                    output[address2] = v
                else:
                    output.pop(address2, None)
        state = output
    return state


def target(c0, c1):
    result = {c0: (1, 0, 0, 0)}
    result[c1] = add(result.get(c1, ZERO), (0, 0, 0, 1))
    return result


def serialized(state):
    return [[list(a), list(n)] for a, n in sorted(state.items())]


def binary_rows(field, n):
    """Restriction of scalars derived from the primary field multiplication table."""
    rows = [0]*4
    for i in range(2):
        for j in range(2):
            for bit in range(2):
                column = field.table[n[2*i+j]][1 << bit]
                for outbit in range(2):
                    rows[2*i+outbit] |= ((column >> outbit) & 1) << (2*j+bit)
    return rows


def binary_serialized(field, state):
    return [[list(a), binary_rows(field, n)] for a, n in sorted(state.items())]


def rational_rank(rows):
    # Only needed for tiny exact integer address fixtures.
    from fractions import Fraction
    a = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        v = a[rank][col]
        a[rank] = [x/v for x in a[rank]]
        for i in range(len(a)):
            if i != rank:
                v = a[i][col]
                a[i] = [x-v*y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def formal_checks(field, cyclic):
    require(rational_rank(FRAMES) == 3, "one rational relation")
    require(rational_rank((*FRAMES, OUTSIDE)) == 4, "outside independence")
    for a in FRAMES:
        require(a[0]*a[3]-a[1]*a[2] == 0 and any(a), "rank-one frame")
    require(expsum(FRAMES[0], FRAMES[1]) == SHIFT
            == expsum(FRAMES[2], FRAMES[3]), "two charged decompositions")
    endpoint = target(SHIFT, SHIFT)
    outside_endpoint = target(expsum(SHIFT, OUTSIDE), SHIFT)
    positives = omissions = allowed = rejected = 0
    witnesses = []
    all_placements = []
    e0 = (1, 0, 0, 0)
    for n in cyclic:
        gates = [(frame, n if i < 2 else add(ID, n))
                 for i, frame in enumerate(FRAMES)]
        for order in permutations(range(4)):
            ordered = [gates[i] for i in order]
            got = word(field, ordered)
            require(got == endpoint, "complementary dirty endpoint")
            positives += 1
            for i in range(4):
                require(word(field, ordered[:i]+ordered[i+1:]) != endpoint,
                        "omitted paid call accepted")
                omissions += 1
            for cut in range(5):
                changed = ordered[:cut]+[(OUTSIDE, e0)]+ordered[cut:]
                state = word(field, changed)
                all_placements.append([binary_rows(field, n), list(order), cut,
                                       binary_serialized(field, state)])
                accepted = state == outside_endpoint
                diagonal = all(v[1] == v[2] == 0 for v in state.values())
                require(accepted == diagonal == (cut in (0, 4)),
                        "outside-gate chronological control")
                if accepted:
                    allowed += 1
                else:
                    rejected += 1
            witnesses.append([list(n), list(order), serialized(got)])
    # Concrete counterexample to carrying the *binary uniqueness lemma* over.
    n = (2, 1, 1, 3)
    require(n in cyclic and add(n, ID) in cyclic, "new F4 cyclic pattern")
    require(n != add(n, ID) and n[1:3] == add(n, ID)[1:3],
            "unique cyclic pattern mutant")
    # A single rank-two scalar call would violate the rank-one tariff.
    mass_alias = word(field, [(FRAMES[0], ID)])
    require(mass_alias == target(FRAMES[0], FRAMES[0]), "rank-two scope control")
    # Reducing address exponents modulo 2 hides a real nonidentity call.
    real = word(field, [(FRAMES[0], e0)])
    require(real != {ZERO: ID}, "formal address call is nontrivial")
    collapsed = {}
    for a, v in real.items():
        key = tuple(x % 2 for x in a)
        collapsed[key] = add(collapsed.get(key, ZERO), v)
    require(collapsed == {ZERO: ID}, "finite address alias control")
    # Diversify the displayed obstruction with the actual assignment seed;
    # coverage above remains exhaustive and does not depend on this choice.
    seed = 17
    selected = cyclic[seed % len(cyclic)]
    order = list(permutations(range(4)))[seed % 24]
    cut = 1 + seed % 3
    gates = [(FRAMES[i], selected if i < 2 else add(ID, selected)) for i in order]
    obstruction = word(field, gates[:cut]+[(OUTSIDE, e0)]+gates[cut:])
    require(any(m[1] or m[2] for m in obstruction.values()), "seeded interior leak")
    return {
        "cyclic_projectors": len(cyclic), "orders_per_projector": 24,
        "full_dirty_endpoints": positives, "rejected_single_omissions": omissions,
        "outside_placements_accepted": allowed,
        "outside_placements_rejected": rejected,
        "witnesses_sha256": digest(witnesses),
        "all_placement_coefficients_binary_sha256": digest(all_placements),
        "rank_one_frames": [list(a) for a in FRAMES],
        "rational_span": 3, "outside_span": 4,
        "cyclic_uniqueness_counterexample": [list(n), list(add(n, ID))],
        "scope_controls": {"rank_two_scalar_call": True,
                           "finite_address_alias": True},
        "seed_selected_interior_obstruction": {
            "projector": list(selected), "frame_order": list(order), "cut": cut,
            "complete_formal_coefficients": serialized(obstruction),
        },
    }


def check_sources(root):
    source_path = HERE / "SOURCES.json"
    source = json.loads(source_path.read_text())
    for row in source["files"]:
        if row["usage"] == "input":
            payload = (root / row["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                    "source mismatch: " + row["path"])
            git_blob = hashlib.sha1(b"blob " + str(len(payload)).encode()
                                    + b"\0" + payload).hexdigest()
            require(git_blob == row["git_blob"], "source Git blob mismatch")
    return hashlib.sha256(source_path.read_bytes()).hexdigest()


def compute(root):
    source_sha = check_sources(root)
    census = []
    cyclic4 = None
    field4 = None
    for degree, polynomial in ((1, 3), (2, 7), (3, 11), (4, 19)):
        f = Field(degree, polynomial)
        entry, cyclic = scalar_census(f)
        census.append(entry)
        if degree == 2:
            field4, cyclic4 = f, cyclic
    formal = formal_checks(field4, cyclic4)
    proc = subprocess.run([sys.executable, "-I", "-B", str(HERE / "independent.py")],
                          check=True, capture_output=True, text=True, timeout=60)
    independent = json.loads(proc.stdout)
    for key in ("full_dirty_endpoints", "rejected_single_omissions",
                "outside_placements_accepted", "outside_placements_rejected"):
        require(formal[key] == independent[key], "independent mismatch: " + key)
    require(independent["projectors"] == 20, "independent inventory mismatch")
    require(census[1]["projectors_binary_sha256"]
            == independent["projectors_binary_sha256"],
            "independent complete-projector inventory mismatch")
    require(formal["all_placement_coefficients_binary_sha256"]
            == independent["all_placement_coefficients_binary_sha256"],
            "independent complete-coefficient stream mismatch")
    return {"schema": "extension-one-relation-finite-evidence/v1",
            "base_commit": "997e6a9ca7b4f95d50e366f61412fd640d72a88a",
            "assignment_seed": 17, "source_manifest_sha256": source_sha,
            "field_censuses": census, "formal_F4": formal,
            "independent_binary_F4": independent,
            "scope": "Finite corroboration of PROOF.md, no new kappa; not an enumeration proof of the theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write-result", action="store_true",
                        help="explicitly regenerate this package's finite receipt")
    args = parser.parse_args()
    result = compute(args.repo_root)
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        expected = json.loads(path.read_text())
        # Compare canonical JSON because integer mapping keys serialize as strings.
        require(canonical(result) == canonical(expected), "RESULT.json mismatch")
    print("PASS_BIT_EXTENSION_ONE_RELATION fields=2,4,8,16 "
          "F4_endpoints=144 omissions=576 interleavings_rejected=432 "
          "binary_engine=agree no_new_kappa")


if __name__ == "__main__":
    main()
