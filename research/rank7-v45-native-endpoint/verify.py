# SPDX-License-Identifier: Apache-2.0
"""Phase-exact native residual and normalized private endpoint for V45 helper249."""

import copy
import gzip
import hashlib
import json
import sys
import types
from pathlib import Path

HELPER = 249
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD_PREFIX = "research/rank7-joint-endframes/data/WORD-"
COMPILER = (
    "research/t74-pure44-kernel-composition/supplier/new/code/borrow/"
    "vendor/clifford/clifford_exact.py"
)
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
INPUTS = {WORD_PREFIX + tag + ".json.gz" for tag in ("base", "extra")} | {
    COMPILER,
    KERNEL,
}
W = [256, 128, 64, 35, 16, 11, 5]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique)


def inputs():
    rows = read_json((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(len(rows) == 6, "source record count")
    pins = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    require(set(pins) == INPUTS, "exact source inventory")
    authenticated = {}
    for name, digest in pins.items():
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, "input byte bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "input SHA256 " + name)
        authenticated[name] = raw
    return authenticated


def load_source(raw, name):
    module = types.ModuleType(name)
    exec(compile(raw, name, "exec"), module.__dict__)
    return module


def span(basis):
    require(type(basis) is list and len(basis) <= 9, "frame shape")
    points = {0}
    for value in basis:
        require(
            type(value) is int and 0 < value < 512 and value not in points,
            "independent frame generator",
        )
        points |= {p ^ value for p in tuple(points)}
    return points


def helper_path(word):
    require(word["helper_final"][str(HELPER)] == W, "V45 endpoint")
    require(str(HELPER) not in word["start_extra"], "zero frame entrance")
    require(all(warp[1] != HELPER for warp in word["warps"]), "helper is not a lender")
    require(HELPER not in word["centers"], "helper is not a center")
    for section in ("precondition", "compensation", "cut", "cleanup"):
        require(
            all(
                HELPER not in (g[1:3] if g[0] == "add" else g[1:2])
                for g in word[section]
            ),
            "no omitted helper scalar events",
        )
    require(
        all(
            HELPER not in (c["source"], c["target"])
            for c in word["initial_corrections"]
        ),
        "no helper correction",
    )
    current, transitions = [], []
    for section in ("A", "B", "restore"):
        require(len(word[section]) <= 10_000, "frame event bound")
        for index, gate in enumerate(word[section]):
            regs = gate[1:3] if gate[0] == "add" else gate[1:2]
            if HELPER not in regs:
                continue
            require(gate[0] in ("add", "scale"), "helper has only scalar gates")
            frame = gate[-1]
            require(span(current) <= span(frame) <= span(W), "monotone helper frame")
            if span(current) == span(frame):
                require(current == frame, "no hidden basis change")
            else:
                transitions.append(
                    {"section": section, "index": index, "old": current, "new": frame}
                )
            current = frame
    if span(current) != span(W):
        transitions.append(
            {"section": "endpoint", "index": HELPER, "old": current, "new": W}
        )
    require(len(transitions) <= 7, "seven total rank units")
    return transitions


def inverse_transpose(circuit):
    result = []
    for gate in circuit:
        kind = gate[0]
        if kind == "C":
            result.append((kind, gate[1], -gate[2]))
        elif kind == "D":
            result.append((kind, gate[1], [(-a) % 4 for a in gate[2]]))
        elif kind == "PH":
            result.append((kind, -gate[1] % 4))
        else:
            require(kind in ("P", "X"), "unitary real or phase primitive")
            result.append(gate)
    return result


def recipe_circuit(kernel, recipe):
    require(kernel.well_formed(recipe["left"]), "left monomial schema")
    result = []
    if recipe["right"] is not None:
        require(kernel.well_formed(recipe["right"]), "right monomial schema")
        result += kernel.monomial(recipe["right"])
    return result + kernel.fourier(recipe["rank"]) + kernel.monomial(recipe["left"])


def native_identity(compiler, kernel, old, new):
    require(span(old) <= span(new), "nested native transition")
    op = (
        compiler.canonical_frame(9, tuple(old))
        .adjoint()
        .then(compiler.canonical_frame(9, tuple(new)))
    )
    recipe, _compiled = compiler.lower_child(op)
    recipe = read_json(json.dumps(recipe))
    require(recipe["rank"] == len(new) - len(old), "native rank difference")
    actual = recipe_circuit(kernel, recipe)
    expected = kernel.adjoint(kernel.canonical_frame(old)) + kernel.canonical_frame(new)
    require(kernel.same_operator(actual, expected), "all512 phase-exact columns")
    require(
        kernel.same_operator(inverse_transpose(actual), inverse_transpose(expected)),
        "all512 inverse-transpose columns",
    )
    if old == [] and new == W:
        wrapped = (
            kernel.adjoint(kernel.monomial(recipe["right"]))
            + expected
            + kernel.adjoint(kernel.monomial(recipe["left"]))
        )
        require(
            kernel.same_operator(wrapped, kernel.fourier(7)),
            "wrapped residual is exactly F7 on all512 columns",
        )
        require(
            kernel.same_operator(inverse_transpose(wrapped), kernel.fourier(7, -1)),
            "inverse-transpose wrapped residual is exactly inverse F7",
        )
    mutant = copy.deepcopy(recipe)
    mutant["left"]["phase"] = (mutant["left"]["phase"] + 1) % 4
    require(
        not kernel.same_operator(recipe_circuit(kernel, mutant), expected),
        "global phase control",
    )
    mutant = copy.deepcopy(recipe)
    if mutant["right"] is not None:
        mutant["right"]["linear_Z4"][0] ^= 2
        require(
            not kernel.same_operator(recipe_circuit(kernel, mutant), expected),
            "input character control",
        )
    return {
        "old": old,
        "new": new,
        "rank": recipe["rank"],
        "recipe": recipe,
        "columns_per_orientation": 512,
    }


def compute():
    raw = inputs()
    endpoint_module = load_source(
        (PACKAGE / "endpoints.py").read_bytes(), "endpoint_covectors"
    )
    compiler = load_source(raw[COMPILER], "authenticated_clifford_compiler")
    kernel = load_source(raw[KERNEL], "authenticated_independent_clifford_kernel")
    providers, recipes = {}, {}
    for tag in ("base", "extra"):
        decoded = gzip.decompress(raw[WORD_PREFIX + tag + ".json.gz"])
        require(len(decoded) <= 8_000_000, "decoded word bound")
        word = read_json(decoded)
        path = helper_path(word)
        for transition in [*path, {"old": [], "new": W}]:
            key = json.dumps([transition["old"], transition["new"]])
            if key not in recipes:
                recipes[key] = native_identity(
                    compiler, kernel, transition["old"], transition["new"]
                )
        providers[tag] = {
            "path": path,
            "normalized_endpoint": endpoint_module.check(word),
            "cleanup_omission_control": endpoint_module.omission_control(word),
        }
    return {
        "schema_version": 1,
        "helper": HELPER,
        "private": 704 + HELPER,
        "terminal_frame": W,
        "providers": providers,
        "native_recipes": list(recipes.values()),
        "scope": (
            "Native helper path/residual and normalized endpoint only; "
            "no complete emitted physical replay or new kappa."
        ),
    }


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = read_json(json.dumps(compute()))
    if sys.argv[1:]:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    require(
        read_json((PACKAGE / "RESULT.json").read_bytes()) == result, "exact receipt"
    )
    print(
        "PASS_RANK7_V45_NATIVE_ENDPOINT helper=249 private=953 "
        "providers=2 columns=512 no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_RANK7_V45_NATIVE_ENDPOINT: {error}") from error
