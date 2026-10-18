#!/usr/bin/env python3
"""Exact compact-control carry audit. Python 3.10+; standard library only.

New code: Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
Apache-2.0. Source interpreter imports occur only in differential_checks().
"""
from __future__ import annotations

import argparse
from array import array
from fractions import Fraction
import hashlib
import importlib
import itertools
import json
from pathlib import Path
import random
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 71


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def highest_step(y, highest, n, K):
    place = 1 << (n * K)
    return y + highest * (1 - 2 * ((y // place) & 1)) * place


def check_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for rel, expected in pins["required_files"].items():
        data = (ROOT / rel).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected["sha256"],
                "source SHA256 mismatch: " + rel)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == expected["git_blob"],
                "source Git blob mismatch: " + rel)
    return len(pins["required_files"])


class Word:
    """Quotient by unused source bits, low rho target bits, and back field.

    y retains EVERY target bit at or above rho, including the unprocessed top
    segment. z is the n-bit vector of low selected source bits. The back field
    cancels in each swap/rotate/swap sandwich, for any initial value.
    """
    def __init__(self, n, K, G, rho):
        require(n >= 1 and G >= 1 and K >= G + 1 and 0 <= rho < K,
                "outside theorem domain")
        self.n, self.K, self.G, self.rho = n, K, G, rho
        self.A, self.B = 1 << (K - 1), 1 << G
        self.ymod = 1 << ((n + 1) * K - rho)
        self.tmod = 1 << (n * G)
        self.yweights = tuple(1 << (K * i) for i in range(n))
        self.tweights = tuple(1 << (G * i) for i in range(n))
        self.tdigits = tuple(tuple((t // w) % self.B for w in self.tweights)
                             for t in range(self.tmod))
        self.packed = tuple(sum(((y // w) & 1) * b
                                for w, b in zip(self.yweights, self.tweights))
                            for y in range(self.ymod))
        self.masks = tuple(sum(((z >> i) & 1) * w
                              for i, w in enumerate(self.yweights))
                           for z in range(1 << n))
        self.offset1 = tuple(tuple(2 * sum(((z >> i) & 1) * d * w
                                          for i, (d, w) in enumerate(zip(ds, self.yweights)))
                                    for ds in self.tdigits)
                             for z in range(1 << n))
        self.offset2 = tuple(tuple(sum(((z >> i) & 1) * (1 - 2 * d) * w
                                        for i, (d, w) in enumerate(zip(ds, self.yweights)))
                                    for ds in self.tdigits)
                             for z in range(1 << n))

    def raw(self, y, t, z):
        y = (y + self.offset1[z][t]) % self.ymod
        t = (t + self.packed[y]) % self.tmod
        y = (y + self.offset2[z][t]) % self.ymod
        t = (t - self.packed[y ^ self.masks[z]]) % self.tmod
        return y, t

    def inverse(self, y, t, z):
        t = (t + self.packed[y ^ self.masks[z]]) % self.tmod
        y = (y - self.offset2[z][t]) % self.ymod
        t = (t - self.packed[y]) % self.tmod
        y = (y - self.offset1[z][t]) % self.ymod
        return y, t

    def nonsaturated(self, t):
        return all(d < self.B - 1 for d in self.tdigits[t])

    def good(self, y, t, z):
        ds = self.tdigits[t]
        return (all(d < self.B - 1 for d in ds) and
                all(((y // self.yweights[i]) >> 1) % self.A
                    + ((z >> i) & 1) * ds[i] < self.A
                    for i in range(self.n - 1)))

    def old_good(self, y, t):
        return (self.nonsaturated(t) and
                all(2 * self.B <= ((y // w) >> 1) % self.A < self.A - 2 * self.B
                    for w in self.yweights))

    def expected_good_fraction(self):
        return (Fraction(self.B - 1, self.B) ** self.n *
                (1 - Fraction(self.B - 2, 4 * self.A)) ** (self.n - 1))

    def carries(self, y, t, z):
        incoming = 0
        rows = []
        radix = 2 * self.A
        for i, (w, d) in enumerate(zip(self.yweights, self.tdigits[t])):
            v = (y // w) % radix
            total = v + 2 * ((z >> i) & 1) * d + incoming
            rows.append([incoming, total // radix])
            incoming = total // radix
        return rows


def permutation_census(parameters):
    w = Word(*parameters)
    size = w.ymod * w.tmod
    counts = dict(states=0, nonsaturated=0, exact_agreement=0,
                  new_good=0, old_good=0, target_only_false_acceptances=0,
                  repaired_records=0, highest_bit_checks=0)
    hashes = [hashlib.sha256(), hashlib.sha256()]
    wrong_key = None
    for z in range(1 << w.n):
        inv = array("i", [-1]) * size
        raw_payload = array("i", [-1]) * size
        bad = []
        for t in range(w.tmod):
            ns = w.nonsaturated(t)
            for y in range(w.ymod):
                sid = t * w.ymod + y
                yy, tt = w.raw(y, t, z)
                oid = tt * w.ymod + yy
                require(inv[oid] == -1, "raw map not injective")
                inv[oid] = sid
                raw_payload[oid] = sid
                require(w.inverse(yy, tt, z) == (y, t), "literal inverse failed")
                target = y ^ w.masks[z]
                correct = (yy, tt) == (target, t)
                good = w.good(y, t, z)
                require(not ns or correct == good, "nonsaturated iff failed")
                require(w.good(target, t, z) == good, "ideal envelope invariance failed")
                require(w.good(yy, tt, z) == good, "raw envelope invariance failed")
                old = w.old_good(y, t)
                require(not old or good, "old envelope not contained in new envelope")
                counts["states"] += 1
                counts["nonsaturated"] += ns
                counts["exact_agreement"] += correct
                counts["new_good"] += good
                counts["old_good"] += old
                counts["target_only_false_acceptances"] += yy == target and tt != t
                if not good:
                    bad.append(sid)
                hashes[0].update(struct.pack("<I", oid))
        require(all(s >= 0 for s in inv), "raw map not surjective")

        # Forward-table inversion is independent of inverse() and of the proof.
        records = []
        wrong = []
        for q in bad:
            source = inv[q]
            t, y = divmod(source, w.ymod)
            key = t * w.ymod + (y ^ w.masks[z])
            records.append((key, raw_payload[q]))
            qt, qy = divmod(q, w.ymod)
            wrong.append((qt * w.ymod + (qy ^ w.masks[z]), raw_payload[q]))
        records.sort()
        require([key for key, _ in records] == bad, "repair keys do not fill exactly the holes")
        repaired = array("i", raw_payload)
        for hole, (_, record) in zip(bad, records):
            repaired[hole] = record
        for t in range(w.tmod):
            for y in range(w.ymod):
                q = t * w.ymod + y
                require(repaired[q] == t * w.ymod + (y ^ w.masks[z]),
                        "repair misplaced a record")
                # Move actual repaired records through the separate highest-bit stage.
                original_t, original_y = divmod(repaired[q], w.ymod)
                for highest in (0, 1):
                    destination = highest_step(y, highest, w.n, w.K)
                    expected_destination = original_y ^ (w.masks[z] | highest << (w.n * w.K))
                    require(original_t == t and destination == expected_destination,
                            "highest selected XOR composition failed")
                    counts["highest_bit_checks"] += 1
                hashes[1].update(struct.pack("<I", repaired[q]))
        counts["repaired_records"] += len(bad)
        if wrong_key is None and z:
            wrong.sort()
            require([key for key, _ in wrong] == bad, "wrong-key control unexpectedly changes holes")
            misplaced = sum(record != repaired[hole]
                            for hole, (_, record) in zip(bad, wrong))
            if misplaced:
                wrong_key = {"z": z, "holes_filled": len(bad), "records_misplaced": misplaced}
    expected = w.expected_good_fraction()
    require(Fraction(counts["new_good"], counts["states"]) == expected,
            "product density disagrees with full census")
    old_fraction = (Fraction(w.B - 1, w.B) *
                    Fraction(max(w.A - 4 * w.B, 0), w.A)) ** w.n
    require(Fraction(counts["old_good"], counts["states"]) == old_fraction,
            "old product density mismatch")
    require(wrong_key is not None, "wrong-key control was vacuous")
    return dict(parameters=dict(zip(("n", "K", "G", "rho"), parameters)),
                quotient="all z, every target bit at/above rho, all compact t; unused source bits, low target bits, and b are spectators",
                counts=counts, good_fraction=str(expected), old_good_fraction=str(old_fraction),
                raw_map_sha256=hashes[0].hexdigest(), repaired_payload_sha256=hashes[1].hexdigest(),
                hash_encoding="z then t then y; little-endian uint32 destination or source index",
                wrong_key_control=wrong_key)


def boundary_census():
    cases = 0
    pairs = 0
    for G in range(1, 6):
        B = 1 << G
        for K in range(G + 1, G + 6):
            A = 1 << (K - 1)
            safe = 0
            for t in range(B - 1):
                for g in range(A):
                    for z in (0, 1):
                        admitted = g + z * t < A
                        safe += admitted
                        for a in (0, 1):
                            v = 2 * g + a
                            first = v + 2 * z * t
                            require((first < 2 * A) == admitted, "carry boundary failed")
                            loaded = t + (first & 1)
                            final = first + z * (1 - 2 * loaded)
                            restored = loaded - ((final & 1) ^ z)
                            require((final, restored) == (v ^ z, t), "integer identity failed")
                            cases += 1
            require(safe == (B - 1) * (2 * A) - (B - 1) * (B - 2) // 2,
                    "local density count failed")
            pairs += 1
    return dict(radix_pairs=pairs, exact_local_cases=cases)


def controls():
    w = Word(2, 3, 2, 2)
    # Source bit 1 is zero: the target is right while the dirty t is wrong.
    state = (6, 1, 1)
    y, t, z = state
    out = w.raw(*state)
    require(out[0] == y ^ w.masks[z] and out[1] != t,
            "target-only observation did not miss a dirty-field failure")
    require(((y >> 1) % w.A) + t == w.A and not w.good(*state),
            "strict guard equality control failed")
    # The same boundary crossing is harmless at the final processed segment.
    last = Word(1, 3, 2, 2)
    require(last.raw(6, 1, 1) == (7, 1) and last.good(6, 1, 1),
            "harmless final carry rejected")
    # Nonsaturation is essential, even with no outgoing target carry.
    saturation = (1, 3, 1)
    sat_out = last.raw(*saturation)
    require(sat_out != (0, 3), "temporary saturation control failed")
    require(last.carries(*saturation)[0][1] == 0, "saturation witness also crossed target boundary")
    # A source-zero segment imposes no guard on its target.
    require(w.raw(6, 2, 0) == (6, 2) and w.good(6, 2, 0),
            "source-zero positive control failed")
    # The new envelope is not the global exact agreement set.
    require(last.raw(1, 3, 0) == (1, 3) and not last.good(1, 3, 0),
            "global failure-support distinction lost")
    # Include a strict real enlargement in a source-domain nonempty old guard.
    production = Word(2, 7, 2, 6)
    require(production.good(0, 1, 1) and not production.old_good(0, 1),
            "lower-guard removal control was vacuous")
    require(production.raw(0, 1, 1) == (1, 1), "newly admitted address wrong")
    top = 1 << (production.n * production.K)
    require(highest_step(1, 1, production.n, production.K) != 1,
            "omitted highest XOR undetected")
    return dict(
        target_only_and_nonstrict_guard={"parameters": [2, 3, 2, 2],
                                       "input_y_t_z": list(state), "output_y_t": list(out),
                                       "ideal_y_t": [7, 1]},
        harmless_final_carry={"input_y_t_z": [6, 1, 1], "output_y_t": [7, 1]},
        temporary_saturation={"input_y_t_z": list(saturation), "output_y_t": list(sat_out)},
        source_zero={"input_y_t_z": [6, 2, 0], "output_y_t": [6, 2]},
        excluded_but_correct={"input_y_t_z": [1, 3, 0], "output_y_t": [1, 3]},
        removed_lower_guard={"parameters": [2, 7, 2, 6], "input_y_t_z": [0, 1, 1]},
        omitted_highest_xor={"expected": 1 | top, "omitted": 1})


def differential_checks():
    # Predecessor executable is a comparison oracle ONLY, not the census engine.
    sys.path.insert(0, str(ROOT / "scripts"))
    source = importlib.import_module("audit_compact_controls")
    rng = random.Random(SEED)
    cases = 0
    domain = [(1, 6, 2, 0), (1, 6, 2, 5), (2, 7, 2, 6),
              (3, 5, 3, 4), (4, 4, 2, 3), (5, 3, 1, 2)]
    for args in domain:
        w = Word(*args)
        n, K, G, rho = args
        width = (n + 1) * K
        for _ in range(256):
            state = {"x": rng.randrange(1 << width), "y": rng.randrange(1 << width),
                     "t": rng.randrange(w.tmod), "b": rng.randrange(w.tmod)}
            z = sum(((state["x"] >> (rho + i * K)) & 1) << i for i in range(n))
            yy, tt = w.raw(state["y"] >> rho, state["t"], z)
            expected = dict(state, y=(yy << rho) | (state["y"] % (1 << rho)), t=tt)
            actual = source.execute(state, n, K, rho, G)
            require(actual == expected, "source differential forward mismatch")
            require(source.execute(actual, n, K, rho, G, inverse=True) == state,
                    "source differential inverse mismatch")
            require(not w.good(state["y"] >> rho, state["t"], z) or
                    actual == source.ideal(state, n, K, rho), "source good map wrong")
            require(source.good(state["y"], state["t"], n, K, rho, G) ==
                    w.old_good(state["y"] >> rho, state["t"]), "source old guard mismatch")
            high = ((state["x"] >> (rho + n * K)) & 1) << (rho + n * K)
            if w.good(state["y"] >> rho, state["t"], z):
                full = state["y"] ^ sum(((state["x"] >> (rho + i * K)) & 1)
                                          << (rho + i * K) for i in range(n + 1))
                require(actual["y"] ^ high == full, "source highest XOR composition failed")
            cases += 1
    return dict(seed=SEED, cases=cases, domains=[list(args) for args in domain],
                scope="sampled full physical source states, including arbitrary back fields; earlier-source only")


def certificate():
    sources = check_sources()
    boundaries = boundary_census()
    domains = [(1, 6, 2, 0), (2, 3, 2, 2), (2, 6, 2, 5),
               (2, 5, 3, 4), (3, 3, 1, 2), (3, 3, 2, 2)]
    censuses = [permutation_census(args) for args in domains]
    fractions = []
    for n, K, G in [(1, 7, 2), (2, 7, 2), (8, 12, 3), (17, 16, 4)]:
        B, A = 1 << G, 1 << (K - 1)
        good = Fraction(B - 1, B) ** n * (1 - Fraction(B - 2, 4 * A)) ** (n - 1)
        union = min(Fraction(1), Fraction(n, B) + Fraction((n - 1) * (B - 2), 4 * A))
        require(1 - good <= union, "repair union bound failed")
        fractions.append(dict(n=n, K=K, G=G, good_fraction=str(good),
                              bad_fraction=str(1 - good), bad_union_bound=str(union)))
    return dict(status="PASS_COMPACT_GUARD_AUDIT", new_kappa=False,
                required_source_files=sources, boundary_census=boundaries,
                permutations=censuses, differential=differential_checks(),
                controls=controls(), density_examples=fractions,
                theorem="On nonsaturated t, full earlier-source correctness iff g_i+z_i*t_i<A for every i<n-1. Last outgoing carry is unrestricted.",
                exact_envelope_density="((B-1)/B)^n * (1-(B-2)/(4*A))^(n-1)",
                scope="Written all-n address proof plus finite exact supporting evidence; no later-source extension, physical compiler, selected-supplier admission, or full multiplication theorem.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a NEW receipt; never overwrite")
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), "refusing to overwrite an existing receipt")
    result = certificate()
    if args.write:
        with args.write.open("x") as handle:
            handle.write(canonical(result))
    else:
        require(result == json.loads((HERE / "EXPECTED.json").read_text()),
                "deterministic receipt mismatch")
    count = sum(c["counts"]["states"] for c in result["permutations"])
    print(f"PASS_COMPACT_GUARD_AUDIT states={count} source_samples={result['differential']['cases']} domains={len(result['permutations'])} no_new_kappa")


if __name__ == "__main__":
    main()
