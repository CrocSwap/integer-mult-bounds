#!/usr/bin/env python3
"""Exact earlier-source agreement and maximal XOR-invariant guard audit.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Credits and mathematical scope are in README.md and PROOF.md.
"""
import argparse
from fractions import Fraction
import hashlib
import importlib
import json
from pathlib import Path
import random
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 69
DOMAINS = ((1, 3, 2, 0), (2, 3, 2, 2), (3, 2, 1, 1),
           (3, 3, 2, 2), (2, 4, 3, 3), (2, 6, 2, 5))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def check_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [pin for pin in pins["files"] if pin["usage"] == "input"]
    for pin in inputs:
        name = pin["path"]
        data = (ROOT / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"],
                "source SHA256 mismatch: " + name)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == pin["git_blob"],
                "source Git blob mismatch: " + name)
    return len(inputs)


class Word:
    """Four whole-register modular updates, independent of the carry test.

    The back field cancels in each swap sandwich. Low rho target bits and
    unselected source bits are spectators; all upper target bits remain.
    """
    def __init__(self, n, K, G, rho):
        require(n >= 1 and G >= 1 and K >= G + 1 and 0 <= rho < K,
                "outside theorem domain")
        self.args = n, K, G, rho
        self.n, self.K, self.G, self.rho = self.args
        self.A, self.B = 1 << (K - 1), 1 << G
        self.Y, self.T = 1 << ((n + 1) * K - rho), 1 << (n * G)
        self.r = tuple(1 << (K * i) for i in range(n))
        self.b = tuple(1 << (G * i) for i in range(n))
        self.digits = tuple(tuple((t // b) % self.B for b in self.b)
                            for t in range(self.T))
        self.pack = tuple(sum(((y // r) & 1) * b for r, b in zip(self.r, self.b))
                          for y in range(self.Y))
        self.mask = tuple(sum(((z >> i) & 1) * r for i, r in enumerate(self.r))
                          for z in range(1 << n))
        self.first = tuple(tuple(2 * sum(((z >> i) & 1) * t * r
                                         for i, (t, r) in enumerate(zip(ds, self.r)))
                                 for ds in self.digits) for z in range(1 << n))
        self.second = tuple(tuple(sum(((z >> i) & 1) * (1 - 2 * t) * r
                                       for i, (t, r) in enumerate(zip(ds, self.r)))
                                  for ds in self.digits) for z in range(1 << n))

    def raw(self, y, t, z):
        y = (y + self.first[z][t]) % self.Y
        t = (t + self.pack[y]) % self.T
        y = (y + self.second[z][t]) % self.Y
        return y, (t - self.pack[y ^ self.mask[z]]) % self.T

    def inverse(self, y, t, z):
        t = (t + self.pack[y ^ self.mask[z]]) % self.T
        y = (y - self.second[z][t]) % self.Y
        t = (t - self.pack[y]) % self.T
        return (y - self.first[z][t]) % self.Y, t

    def predicates(self, y, t, z):
        """Return exact agreement, invariant core, and PR1219 guard."""
        carry = 0
        agree = core = previous = True
        for i, ti in enumerate(self.digits[t]):
            v = (y >> (self.K * i)) % (2 * self.A)
            zi = (z >> i) & 1
            outgoing = (ti + (v & 1) + carry) // self.B
            interior = i == self.n - 1 or v // 2 + zi * ti < self.A
            agree &= interior and (not zi or (carry == outgoing == 0))
            core &= interior and (not zi or (carry == 0 and ti < self.B - 1))
            previous &= interior and ti < self.B - 1
            carry = outgoing
        return bool(agree), bool(core), bool(previous)


def transfer_matrix(A, B, interior, core):
    if core:
        top = A * (4 * B - 3) - ((B - 1) * (B - 2) if interior else 0)
    else:
        top = 2 * A * (2 * B - 1) - ((B - 1) ** 2 if interior else 0)
    return ((top, A), (A * (2 * B - 3), 3 * A))


def density(n, K, G, core):
    A, B = 1 << (K - 1), 1 << G
    row = (1, 0)
    for i in range(n):
        m = transfer_matrix(A, B, i < n - 1, core)
        row = tuple(sum(row[j] * m[j][k] for j in range(2)) for k in range(2))
    return Fraction(sum(row), (4 * A * B) ** n)


def check_matrices():
    """Literal one-digit enumeration, including each incoming/outgoing carry."""
    cases = 0
    for G in range(1, 5):
        B = 1 << G
        for K in range(G + 1, G + 4):
            A = 1 << (K - 1)
            for interior in (False, True):
                matrices = [[[0, 0], [0, 0]] for _ in range(2)]
                for d in (0, 1):
                    for t in range(B):
                        for a in (0, 1):
                            e = (t + a + d) // B
                            for z in (0, 1):
                                for g in range(A):
                                    target = not interior or g + z * t < A
                                    if target and (not z or d == e == 0):
                                        matrices[0][d][e] += 1
                                    if target and (not z or (d == 0 and t < B - 1)):
                                        matrices[1][d][e] += 1
                                    cases += 1
                for core in (False, True):
                    require(tuple(map(tuple, matrices[core])) ==
                            transfer_matrix(A, B, interior, core), "transition count mismatch")
    return cases


def census(args):
    w = Word(*args)
    total = w.Y * w.T
    counts = dict(states=0, agreement=0, invariant_core=0, previous_guard=0,
                  agreement_not_invariant=0, target_only_false_accept=0,
                  unsafe_agreement_repair=0)
    digest = hashlib.sha256()
    for z in range(1 << w.n):
        permutation, agreed, core = [], bytearray(total), bytearray(total)
        seen = bytearray(total)
        for y in range(w.Y):
            for t in range(w.T):
                index = y * w.T + t
                yy, tt = w.raw(y, t, z)
                destination = yy * w.T + tt
                require(not seen[destination], "raw map is not a permutation")
                seen[destination] = 1
                require(w.inverse(yy, tt, z) == (y, t), "inverse mismatch")
                actual = (yy, tt) == (y ^ w.mask[z], t)
                a, h, old = w.predicates(y, t, z)
                require(a == actual, "full-map agreement criterion mismatch")
                require(not old or h, "previous guard escaped invariant core")
                agreed[index], core[index] = a, h
                permutation.append(destination)
                counts["agreement"] += a
                counts["invariant_core"] += h
                counts["previous_guard"] += old
                counts["target_only_false_accept"] += yy == y ^ w.mask[z] and tt != t
                digest.update(struct.pack("<QBBB", destination, a, h, old))
        # Compare to the definition A intersect T(A), not the carry formula.
        # Repair unique payload=index at its CURRENT raw output address.
        repaired = [-1] * total
        records, holes = [], []
        for index, destination in enumerate(permutation):
            ideal = index ^ (w.mask[z] * w.T)
            require(bool(core[index]) == bool(agreed[index] and agreed[ideal]),
                    "maximal invariant subset mismatch")
            require(core[index] == core[ideal] == core[destination], "guard not invariant")
            counts["agreement_not_invariant"] += agreed[index] != agreed[ideal]
            if core[destination]:
                repaired[destination] = index
            else:
                holes.append(destination)
                records.append((ideal, index))
            counts["unsafe_agreement_repair"] += agreed[destination] and destination != ideal
        records.sort()
        require([key for key, _ in records] == sorted(holes), "repair keys do not fill holes")
        for key, payload in records:
            repaired[key] = payload
        for key, payload in enumerate(repaired):
            require(payload == key ^ (w.mask[z] * w.T), "sorted repair payload mismatch")
            digest.update(struct.pack("<Q", payload))
        counts["states"] += total
    for name, mode in (("agreement", False), ("invariant_core", True)):
        require(Fraction(counts[name], counts["states"]) == density(w.n, w.K, w.G, mode),
                "matrix density differs from full permutation census")
    previous = Fraction(w.B - 1, w.B) ** w.n * (1 - Fraction(w.B - 2, 4 * w.A)) ** (w.n - 1)
    require(Fraction(counts["previous_guard"], counts["states"]) == previous,
            "predecessor guard density mismatch")
    return dict(parameters=list(args), counts=counts,
                agreement_fraction=str(density(w.n, w.K, w.G, False)),
                invariant_fraction=str(density(w.n, w.K, w.G, True)),
                previous_fraction=str(previous), map_and_repair_sha256=digest.hexdigest())


def controls():
    one, two = Word(1, 3, 2, 2), Word(2, 3, 2, 2)
    fixtures = [
        ("agreement_without_invariance", one, (0, 3, 1), (1, 3), (True, False, False)),
        ("return_is_wrong", one, (1, 3, 1), (8, 3), (False, False, False)),
        ("compact_carry_into_active_digit", two, (1, 3, 2), (121, 3), (False, False, False)),
        ("target_only_false_accept", two, (6, 1, 1), (7, 5), (False, False, False)),
        ("harmless_final_target_carry", one, (6, 1, 1), (7, 1), (True, True, True)),
        ("harmless_final_compact_carry", one, (1, 3, 0), (1, 3), (True, True, False)),
        ("saturated_zero_source_admitted", two, (0, 3, 2), (8, 3), (True, True, False)),
    ]
    result = []
    for name, w, state, expected, flags in fixtures:
        require(w.raw(*state) == expected, "control map failed: " + name)
        require(w.predicates(*state) == flags, "control predicate failed: " + name)
        result.append(dict(name=name, parameters=list(w.args), input=list(state),
                           output=list(expected), agreement=flags[0], invariant=flags[1]))
    require(one.predicates(8, 3, 1)[0], "unsafe current-address repair control vacuous")
    require(density(2, 6, 2, True) == Fraction(1499, 2048), "headline fraction mismatch")
    return result


def physical_checks():
    sys.path.insert(0, str(ROOT / "scripts"))
    source = importlib.import_module("audit_compact_controls")
    rng = random.Random(SEED)
    domains = ((1, 3, 2, 0), (2, 3, 2, 2), (3, 3, 2, 1),
               (4, 2, 1, 1), (2, 6, 2, 5), (2, 7, 3, 0))
    count = core_count = 0
    digest = hashlib.sha256()
    for args in domains:
        w = Word(*args)
        width = (w.n + 1) * w.K
        for trial in range(256):
            state = dict(x=rng.randrange(1 << width), y=rng.randrange(1 << width),
                         t=rng.randrange(w.T), b=rng.randrange(w.T))
            # Half the samples stress a saturated temporary digit.
            if trial % 2:
                i = rng.randrange(w.n)
                state["t"] |= (w.B - 1) << (i * w.G)
            z = sum(((state["x"] >> (w.rho + i * w.K)) & 1) << i for i in range(w.n))
            y, t = w.raw(state["y"] >> w.rho, state["t"], z)
            expected = dict(state, y=(y << w.rho) | (state["y"] % (1 << w.rho)), t=t)
            actual = source.execute(state, w.n, w.K, w.rho, w.G)
            require(actual == expected, "physical forward mismatch")
            require(source.execute(actual, w.n, w.K, w.rho, w.G, inverse=True) == state,
                    "physical inverse mismatch")
            agreement, core, _ = w.predicates(state["y"] >> w.rho, state["t"], z)
            require(agreement == (actual == source.ideal(state, w.n, w.K, w.rho)),
                    "physical complete-map agreement mismatch")
            if not w.predicates(actual["y"] >> w.rho, actual["t"], z)[1]:
                actual = source.ideal(source.execute(actual, w.n, w.K, w.rho, w.G,
                                                     inverse=True), w.n, w.K, w.rho)
            require(actual == source.ideal(state, w.n, w.K, w.rho), "physical repair mismatch")
            high = ((state["x"] >> (w.rho + w.n * w.K)) & 1) << (w.rho + w.n * w.K)
            complete = dict(actual, y=actual["y"] ^ high)
            full_mask = sum(((state["x"] >> (w.rho + i * w.K)) & 1) << (w.rho + i * w.K)
                            for i in range(w.n + 1))
            require(complete == dict(state, y=state["y"] ^ full_mask), "highest-bit completion failed")
            digest.update(canonical([state, complete]).encode())
            count += 1
            core_count += core
    return dict(seed=SEED, cases=count, invariant_cases=core_count,
                domains=[list(d) for d in domains], payload_sha256=digest.hexdigest())


def certificate():
    return dict(status="PASS_COMPACT_SATURATION_AUDIT", seed=SEED,
                source_files=check_sources(), transition_cases=check_matrices(),
                controls=controls(), domains=[census(d) for d in DOMAINS],
                physical=physical_checks(), no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print deterministic certificate")
    args = parser.parse_args()
    result = certificate()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text())),
                "saved result mismatch")
        print("PASS_COMPACT_SATURATION_AUDIT states=" + str(sum(d["counts"]["states"] for d in result["domains"]))
              + " physical=" + str(result["physical"]["cases"]) + " controls=" + str(len(result["controls"]))
              + " headline=1499/2048 no_new_kappa")


if __name__ == "__main__":
    main()
