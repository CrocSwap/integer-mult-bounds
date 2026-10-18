#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite native lowering of a literal fragment transport witness.

The compiler and independent Gaussian interpreter are retained from the P104
native channel (PR1991), with their predecessor attribution and notices. This
does not supply a backward interface, global hosting, or recursive precision.
"""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "compiler": ("research/p104-native-channel/vendor/clifford_exact.py",
                 "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"),
    "interpreter": ("research/p104-native-channel/vendor/native_verify.py",
                    "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    relative, digest = INPUTS[name]
    path = ROOT / relative
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "native source drift: " + relative)
    spec = importlib.util.spec_from_file_location("p104_fragment_native_" + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def span(basis):
    values = {0}
    for x in basis:
        require(isinstance(x, int) and 0 < x < 512, "invalid native frame vector")
        values |= {x ^ y for y in tuple(values)}
    require(len(values) == 1 << len(basis), "dependent native frame basis")
    return frozenset(values)


def verify(witness):
    compiler, interpreter = load("compiler"), load("interpreter")
    edges = witness["transports"]
    require(bool(edges), "empty literal transport witness")
    frames, recipes, profile = {}, {}, Counter()

    @lru_cache(None)
    def chart(basis):
        return compiler.canonical_frame(9, basis)

    def key(edge):
        return tuple(edge["old"]), tuple(edge["new"])

    for edge in edges:
        old, new = key(edge)
        old_span, new_span = span(old), span(new)
        for basis, subspace in ((old, old_span), (new, new_span)):
            require(frames.setdefault(subspace, basis) == basis, "inconsistent chart basis for one subspace")
        require(old_span < new_span or new_span < old_span, "transport is not a strict nested frame change")
        rank = abs(len(new) - len(old))
        require(edge["rank"] == rank, "declared occurrence rank differs from frame jump")
        profile[rank] += 1
        if (old, new) in recipes:
            continue
        record, _ = compiler.lower_child(chart(old).adjoint().then(chart(new)))
        require(record["rank"] == rank, "native rank differs from literal frame jump")
        expected = interpreter.adjoint(interpreter.frame(old, 9)) + interpreter.frame(new, 9)
        interpreter.equal(interpreter.recipe(record), expected, "literal fragment transport")
        recipes[old, new] = record

    ports = witness["ports"]
    require(len(ports) == len(set(ports)) == 104, "104 distinct native ports")
    adapters = []
    for normal in ports:
        require(0 < normal < 512 and normal.bit_count() % 2 == 1, "nonodd intrinsic port")
        entry = (normal,)
        hyperplane = frozenset(x for x in range(512) if not (x & normal).bit_count() % 2)
        require(hyperplane in frames, "missing literal target endpoint chart")
        exit_frame = frames[hyperplane]
        for where, actual, expected in (
            ("entry", compiler.cgate(9, normal, 1).adjoint().then(chart(entry)),
             interpreter.adjoint((("C", normal, 1),)) + interpreter.frame(entry, 9)),
            ("exit", chart(exit_frame).adjoint().then(compiler.cgate(9, normal, -1).then(compiler.fourier(9))),
             interpreter.adjoint(interpreter.frame(exit_frame, 9)) + (("C", normal, -1),) + interpreter.fourier(9)),
        ):
            record, _ = compiler.lower_child(actual)
            require(record["rank"] == 0, "intrinsic endpoint adapter has positive rank")
            interpreter.equal(interpreter.recipe(record), expected, "fragment intrinsic endpoint")
            adapters.append({"normal": normal, "position": where, "recipe": record})

    private_paths = witness.get("private_paths", [witness.get("private_transports", [])])
    require(bool(private_paths) and all(private_paths), "missing private descent witness")
    require([edge for path in private_paths for edge in path] ==
            [edge for edge in edges if edge["private"]], "private path occurrence coverage mismatch")
    gaussian_columns = 0
    for private in private_paths:
        private_actual = ()
        for i, edge in enumerate(private):
            old, new = key(edge)
            require((old, new) in recipes, "private edge missing from literal occurrences")
            require(span(new) < span(old), "private path is not descending")
            if i:
                require(tuple(private[i - 1]["new"]) == old, "discontinuous private path")
                require(private[i - 1]["register"] == edge["register"], "private path changes owned register")
            private_actual += interpreter.recipe(recipes[old, new])
        first, last = tuple(private[0]["old"]), tuple(private[-1]["new"])
        require((len(first), len(last)) == (8, 1), "expected complete rank-seven private path")
        private_expected = interpreter.adjoint(interpreter.frame(first, 9)) + interpreter.frame(last, 9)
        interpreter.equal(private_actual, private_expected, "composed private path")
        for column in range(512):
            require(interpreter.state(private_actual, column) == interpreter.state(private_expected, column),
                    "private path Gaussian basis column")
            gaussian_columns += 1

    one_key = next(iter(recipes))
    bad = deepcopy(recipes[one_key])
    bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    old, new = one_key
    try:
        interpreter.equal(interpreter.recipe(bad),
                          interpreter.adjoint(interpreter.frame(old, 9)) + interpreter.frame(new, 9),
                          "corrupted native phase")
    except ValueError:
        pass
    else:
        raise ValueError("wrong global phase accepted")
    canonical = [{"old": a, "new": b, "recipe": recipes[a, b]} for a, b in sorted(recipes)]
    return {
        "status": "PASS_FINITE_NATIVE_LOWERING",
        "literal_transport_occurrences": len(edges),
        "distinct_transport_recipes": len(recipes),
        "paid_profile": {str(k): v for k, v in sorted(profile.items())},
        "native_rank_mass": sum(k * v for k, v in profile.items()),
        "intrinsic_monomial_endpoint_adapters": len(adapters),
        "private_paths": len(private_paths),
        "private_path_gaussian_columns": gaussian_columns,
        "every_recipe_signed_pauli_action_and_global_phase_checked": True,
        "recipe_payload_sha256": hashlib.sha256(json.dumps(canonical + adapters, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "wrong_global_phase_control_rejected": True,
        "scope": "Finite forward operators for the supplied literal scalar/frame witness; its endpoint identity is checked separately. No backward supplier, hosting, precision, or kappa claim.",
    }
