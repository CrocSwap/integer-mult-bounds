#!/usr/bin/env python3
"""Exact bounded audit of phase-weighted retained Fourier layouts.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Explicit exceptions preserve all checks under Python -O.
"""

import argparse
from fractions import Fraction
import hashlib
import importlib.util
from itertools import permutations, product
import json
from math import lcm, prod
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("weighted_fourier_oracle", HERE / "oracle.py")
ORACLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLE)
SEED = 71
DOMAIN = ((2,), (3,), (4,), (2, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Group:
    def __init__(self, moduli):
        require(bool(moduli) and all(type(q) is int and q >= 2 for q in moduli),
                "cyclic moduli must be integers at least two")
        self.moduli = tuple(moduli)
        self.points = tuple(product(*(range(q) for q in moduli)))
        self.index = {x: i for i, x in enumerate(self.points)}
        self.n = prod(moduli)
        self.m = lcm(4, *moduli)
        self.pair = tuple(tuple(sum(a * b * (self.m // q)
                         for a, b, q in zip(x, y, moduli)) % self.m
                         for y in self.points) for x in self.points)
        self.generators = tuple(self.index[tuple(int(i == j) for i in range(len(moduli)))]
                                for j in range(len(moduli)))

    def subtract(self, x, y):
        return self.index[tuple((a - b) % q
                               for a, b, q in zip(self.points[x], self.points[y], self.moduli))]

    def fractional_character(self, x, y):
        # Rational turns, independent of the scaled character table.
        turn = sum((Fraction(a * b, q)
                    for a, b, q in zip(self.points[x], self.points[y], self.moduli)), Fraction())
        scaled = self.m * turn
        require(scaled.denominator == 1, "character denominator mismatch")
        return int(scaled) % self.m


def validate_layout(g, pi, sigma, rho, alpha, beta, omega):
    for p in (pi, sigma, rho):
        require(len(p) == g.n and all(type(x) is int for x in p)
                and sorted(p) == list(range(g.n)), "layout must be a permutation")
    for phases in (alpha, beta, omega):
        require(len(phases) == g.n and all(type(x) is int and 0 <= x < g.m for x in phases),
                "phase exponents must be canonical integers")


def coefficient_condition(g, pi, rho, q, omega):
    """Literal all-entry condition after the forward permutations agree."""
    for x in range(g.n):
        for y in range(g.n):
            if (omega[x] + q[y] + g.pair[rho[x]][y] - g.pair[x][pi[y]]) % g.m:
                return False
    return True


def admit(g, pi, sigma, rho, alpha, beta, omega):
    validate_layout(g, pi, sigma, rho, alpha, beta, omega)
    if tuple(pi) != tuple(sigma):
        return False
    return coefficient_condition(g, pi, rho,
                                 tuple((a + b) % g.m for a, b in zip(alpha, beta)), omega)


def affine_dual(g, pi, rho):
    """Generator reconstruction; return inverse/forward offsets or None."""
    b, a = pi[0], rho[0]
    columns = tuple(g.points[g.subtract(pi[e], b)] for e in g.generators)
    if any((g.moduli[j] * columns[j][i]) % g.moduli[i]
           for j in range(len(columns)) for i in range(len(columns))):
        return None
    for y, point in enumerate(g.points):
        image = tuple((g.points[b][i] + sum(point[j] * columns[j][i]
                                           for j in range(len(columns)))) % g.moduli[i]
                      for i in range(len(columns)))
        if image != g.points[pi[y]]:
            return None
    for x, point in enumerate(g.points):
        adjoint = []
        for j, order in enumerate(g.moduli):
            coordinate = order * sum((Fraction(point[i] * columns[j][i], g.moduli[i])
                                      for i in range(len(columns))), Fraction())
            if coordinate.denominator != 1:
                return None
            adjoint.append((int(coordinate) + g.points[a][j]) % order)
        if tuple(adjoint) != g.points[rho[x]]:
            return None
    return a, b


def normal_form_condition(g, pi, sigma, rho, alpha, beta, omega):
    validate_layout(g, pi, sigma, rho, alpha, beta, omega)
    if tuple(pi) != tuple(sigma):
        return False
    offsets = affine_dual(g, pi, rho)
    if offsets is None:
        return False
    a, b = offsets
    q = tuple((x + y) % g.m for x, y in zip(alpha, beta))
    gamma = q[0]
    return (q == tuple((gamma - g.fractional_character(a, y)) % g.m for y in range(g.n))
            and omega == tuple((-gamma + g.fractional_character(x, b)) % g.m
                               for x in range(g.n)))


def split_product(g, q, salt=0):
    # Only the product of the two forward phases is constrained.
    alpha = tuple((SEED + salt + (j + 1) ** 2 + 3 * j) % g.m for j in range(g.n))
    beta = tuple((q[j] - alpha[j]) % g.m for j in range(g.n))
    return alpha, beta


def checked_basis_pairs(oracle, layout):
    for i in range(oracle.n):
        for j in range(oracle.n):
            actual, expected = oracle.evaluate(oracle.basis(i), oracle.basis(j), **layout)
            require(actual == expected, f"literal convolution failed on bases {i},{j}")
    return oracle.n ** 2


def census_group(moduli):
    g = Group(moduli)
    oracle = ORACLE.FourierOracle(moduli)
    ps = tuple(permutations(range(g.n)))
    weights = tuple(product(range(g.m), repeat=g.n))
    digest = hashlib.sha256()
    reduced = accepted = basis_pairs = 0
    for pi in ps:
        for rho in ps:
            offsets = affine_dual(g, pi, rho)
            structural_q = None
            if offsets is not None:
                a, b = offsets
                structural_q = tuple(-g.fractional_character(a, y) % g.m for y in range(g.n))
                structural_c = tuple(g.fractional_character(x, b) for x in range(g.n))
            for q in weights:
                # y=0 forces the inverse weight, without any affine assumption.
                omega = tuple((g.pair[x][pi[0]] - q[0]) % g.m for x in range(g.n))
                literal = coefficient_condition(g, pi, rho, q, omega)
                normal = (structural_q is not None
                          and q == tuple((q[0] + z) % g.m for z in structural_q)
                          and omega == tuple((z - q[0]) % g.m for z in structural_c))
                require(literal == normal, "matrix / generator classification discrepancy")
                reduced += 1
                digest.update(bytes(pi + rho + q + omega + (int(literal),)))
                if literal:
                    accepted += 1
                    alpha, beta = split_product(g, q, accepted)
                    layout = dict(pi=pi, sigma=pi, rho=rho, alpha=alpha, beta=beta, omega=omega)
                    require(normal_form_condition(g, **layout), "split-product classification failed")
                    basis_pairs += checked_basis_pairs(oracle, layout)
    shared = shared_accepted = 0
    shared_digest = hashlib.sha256()
    for pi in ps:
        structural = affine_dual(g, pi, pi)
        for w in weights:
            q = tuple(2 * t % g.m for t in w)
            omega = tuple(-t % g.m for t in w)
            literal = coefficient_condition(g, pi, pi, q, omega)
            predicted = (all(t == 0 for t in w) and structural == (0, 0))
            require(literal == predicted, "shared-routine rigidity discrepancy")
            shared += 1
            shared_accepted += int(literal)
            shared_digest.update(bytes(pi + w + (int(literal),)))
    mismatched = 0
    mismatch_digest = hashlib.sha256()
    for pi in ps:
        for sigma in ps:
            if pi == sigma:
                continue
            y = next(i for i in range(g.n) if pi[i] != sigma[i])
            q = tuple((SEED + i) % g.m for i in range(g.n))
            alpha, beta = split_product(g, q)
            layout = dict(pi=pi, sigma=sigma, rho=tuple(range(g.n)),
                          alpha=alpha, beta=beta, omega=q)
            require(not admit(g, **layout), "mismatched forward layouts admitted")
            actual, expected = oracle.evaluate(oracle.character(pi[y]), oracle.character(sigma[y]), **layout)
            require(all(not any(z) for z in expected), "off-diagonal convolution should vanish")
            require(all(any(z) for z in actual), "mismatched spectral witness should be nonzero")
            mismatched += 1
            mismatch_digest.update(json.dumps([pi, sigma, actual], separators=(",", ":")).encode())
    return {"moduli": list(moduli), "phase_order": g.m,
            "reduced_candidates": reduced, "accepted": accepted,
            "classification_sha256": digest.hexdigest(), "literal_basis_pairs": basis_pairs,
            "shared_routine_candidates": shared, "shared_routine_accepted": shared_accepted,
            "shared_classification_sha256": shared_digest.hexdigest(),
            "mismatched_forward_pairs": mismatched, "mismatch_sha256": mismatch_digest.hexdigest()}


def make_affine_layout(moduli, linear, a, b, gamma=SEED):
    g = Group(moduli)
    pi = tuple(g.index[tuple((u + v) % q for u, v, q in zip(linear(x), b, moduli))]
               for x in g.points)
    columns = [linear(g.points[e]) for e in g.generators]
    rho = []
    for x in g.points:
        point = []
        for j, order in enumerate(moduli):
            entry = order * sum((Fraction(x[i] * columns[j][i], moduli[i])
                                 for i in range(len(moduli))), Fraction())
            require(entry.denominator == 1, "invalid dual map")
            point.append((int(entry) + a[j]) % order)
        rho.append(g.index[tuple(point)])
    ai, bi = g.index[tuple(a)], g.index[tuple(b)]
    q = tuple((gamma - g.pair[ai][y]) % g.m for y in range(g.n))
    omega = tuple((-gamma + g.pair[x][bi]) % g.m for x in range(g.n))
    alpha, beta = split_product(g, q)
    return g, dict(pi=pi, sigma=pi, rho=tuple(rho), alpha=alpha, beta=beta, omega=omega)


def additional_fixtures():
    specs = [
        ((2, 4), lambda x: ((x[0] + x[1]) % 2, x[1]), (1, 3), (0, 1)),
        ((2, 3), lambda x: (x[0], 2 * x[1] % 3), (1, 2), (1, 1)),
        ((3, 3), lambda x: ((x[0] + x[1]) % 3, x[1]), (2, 1), (1, 2)),
        ((4, 4), lambda x: ((x[0] + x[1]) % 4, x[1]), (3, 1), (1, 3)),
        ((5,), lambda x: (2 * x[0] % 5,), (0,), (0,)),
    ]
    receipts = []
    fixtures = []
    for moduli, linear, a, b in specs:
        g, layout = make_affine_layout(moduli, linear, a, b)
        require(admit(g, **layout) and normal_form_condition(g, **layout), "affine fixture rejected")
        oracle = ORACLE.FourierOracle(moduli)
        count = checked_basis_pairs(oracle, layout)
        actual, expected = oracle.evaluate(oracle.dense(SEED, 1), oracle.dense(SEED, 9), **layout)
        require(actual == expected, "dense affine fixture failed")
        receipts.append({"moduli": list(moduli), "phase_order": g.m,
                         "layout": layout, "literal_basis_pairs": count,
                         "dense_output_numerator": actual, "common_denominator": g.n ** 3})
        fixtures.append((g, layout))
    return receipts, fixtures


def semantic_controls(fixtures):
    g = Group((4,))
    identity = tuple(range(4))
    zeros = (0,) * 4
    controls = []

    def reject(name, group, layout, **options):
        if not options:
            require(not admit(group, **layout), f"admission accepted {name}")
        witness = ORACLE.FourierOracle(group.moduli).first_basis_failure(**layout, **options)
        require(witness is not None, f"no exact convolution witness for {name}")
        controls.append({"name": name, "moduli": list(group.moduli),
                         "layout": layout, "options": options, "witness": witness})

    for name, pi, w in [
            ("constant_i_shared_routine", identity, (1,) * 4),
            ("nonconstant_character_shared_routine", identity, (0, 1, 2, 3)),
            ("phase_compensated_translation_shared_routine", (1, 2, 3, 0), (0, 3, 2, 1))]:
        reject(name, g, dict(pi=pi, sigma=pi, rho=pi, alpha=w, beta=w,
                            omega=tuple(-x % 4 for x in w)))
    ag, valid = fixtures[0]
    # Reverse the character, keeping gamma^-1 fixed at the zero coordinate.
    wrong = dict(valid, omega=tuple((-2 * SEED - x) % ag.m for x in valid["omega"]))
    reject("inverse_character_wrong_sign", ag, wrong)
    # Keep the correct inverse offset (1,3); change only L^dagger to L.
    wrong_rho = tuple(ag.index[((x + y + 1) % 2, (y + 3) % 4)] for x, y in ag.points)
    wrong = dict(valid, rho=wrong_rho)
    reject("reuse_forward_linear_map_as_adjoint", ag, wrong)
    wrong = dict(valid, beta=tuple((x + (i == 1)) % ag.m for i, x in enumerate(valid["beta"])))
    reject("uncompensated_one_operand_phase", ag, wrong)
    wrong = dict(valid, sigma=tuple(reversed(valid["sigma"])))
    reject("different_forward_addresses", ag, wrong)
    plain = dict(pi=identity, sigma=identity, rho=identity, alpha=zeros, beta=zeros, omega=zeros)
    reject("wrong_inverse_fourier_sign", g, plain, inverse_sign=-1)
    reject("missing_one_normalization", g, plain, expected_scale=g.n ** 2)
    return controls


def check_sources(root=None):
    root = HERE.parents[1] if root is None else Path(root)
    pins = json.loads((HERE / "SOURCES.json").read_text())
    checked = {}
    for item in pins["files"]:
        if item["usage"] != "input":
            continue
        digest = hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
        require(digest == item["sha256"], f"source drift: {item['path']}")
        checked[item["path"]] = digest
    manifest = json.loads((root / "upstream/manifest.json").read_text())
    require(manifest["commit"] == "adc7f1241b42e322a6451854ab7e4b4c146bf78a", "upstream commit changed")
    require(manifest["files"]["build/sections/07-resampling.tex"]["sha256"]
            == checked["upstream/build/sections/07-resampling.tex"], "manifest/source mismatch")
    return checked


def build_receipt():
    sources = check_sources()
    groups = [census_group(moduli) for moduli in DOMAIN]
    extras, fixtures = additional_fixtures()
    controls = semantic_controls(fixtures)
    return {"schema_version": 1, "status": "PASS_WEIGHTED_FOURIER_LAYOUT",
            "assignment_seed": SEED, "sources": sources,
            "scope": "Exact algebraic admission only; written universal proof, bounded finite replay, no new kappa.",
            "census": groups, "additional_fixtures": extras, "semantic_controls": controls,
            "totals": {"reduced_candidates": sum(x["reduced_candidates"] for x in groups),
                       "accepted": sum(x["accepted"] for x in groups),
                       "shared_routine_candidates": sum(x["shared_routine_candidates"] for x in groups),
                       "shared_routine_accepted": sum(x["shared_routine_accepted"] for x in groups),
                       "mismatched_forward_pairs": sum(x["mismatched_forward_pairs"] for x in groups),
                       "literal_basis_pairs": sum(x["literal_basis_pairs"] for x in groups + extras),
                       "dense_pairs": len(extras), "semantic_controls": len(controls)}}


def canonical(receipt):
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuses overwrite")
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), "refusing to overwrite receipt")
    receipt = build_receipt()
    text = canonical(receipt)
    if args.write:
        with args.write.open("x") as handle:
            handle.write(text)
    else:
        require((HERE / "EXPECTED.json").read_text() == text, "expected receipt differs")
    print(receipt["status"] + " " + json.dumps(receipt["totals"], sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"FAIL_WEIGHTED_FOURIER_LAYOUT: {exc}", file=sys.stderr)
        sys.exit(1)
