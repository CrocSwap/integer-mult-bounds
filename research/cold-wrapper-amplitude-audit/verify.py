#!/usr/bin/env python3
"""Exact all-column audit of the selected cold residual wrappers.

Standard library only. No producer, Clifford tableau or circuit imports.
Contributor: BigCactusLabs, with OpenAI Codex assistance.
Apache-2.0; see NOTICE.md and README.md for scope and predecessor credit.
"""

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 9
SIZE = 1 << N
SEED = 60
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def parity(x):
    return x.bit_count() % 2


def times_i(z, exponent):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def multiply(z, w):
    a, b = z
    c, d = w
    return a * c - b * d, a * d + b * c


def fourier_numerators(width):
    """Tensor coefficients of ((1+i)I + (1-i)X)/2, denominator 2^width."""
    values = [(1, 0)]
    for _ in range(width):
        values = [multiply(z, (1, 1)) for z in values] + [
            multiply(z, (1, -1)) for z in values
        ]
    return values


def span_coordinates(columns):
    """Enumerate a binary span, without row reduction or matrix inversion."""
    table = {0: 0}
    for i, vector in enumerate(columns):
        require(0 < vector < SIZE, "Frame vector out of range")
        require(vector not in table, "Dependent frame vectors")
        table.update({x ^ vector: mask | (1 << i) for x, mask in list(table.items())})
    return table


def frame_kernel(frame):
    """Direct kernel of K C_[r] K*, where K = D_Q P_G.

    G has the ordered frame vectors as its first columns, completed by
    e_0,...,e_8. Q = I + (G^-1)^T G^-1 over F_2. The inverse coordinates
    are obtained by enumerating all 512 vectors, not by importing G or Q.
    """
    width = len(frame)
    require(width == 4, "This audit is restricted to four-dimensional cold ends")
    coordinates = span_coordinates(frame)
    displacements = [0] * (1 << width)
    for vector, mask in coordinates.items():
        displacements[mask] = vector
    columns = list(frame)
    for i in range(N):
        if (1 << i) not in coordinates:
            columns.append(1 << i)
            coordinates = span_coordinates(columns)
    require(len(coordinates) == SIZE, "Incomplete canonical basis")
    inverse_columns = [coordinates[1 << i] for i in range(N)]
    phases = []
    for x in range(SIZE):
        active = [i for i in range(N) if x & (1 << i)]
        diagonal = sum(1 ^ parity(inverse_columns[i]) for i in active)
        cross = sum(
            parity(inverse_columns[i] & inverse_columns[j])
            for i in active for j in active if i < j
        )
        phases.append((diagonal + 2 * cross) % 4)
    amplitudes = fourier_numerators(width)
    return [
        {x ^ delta: times_i(amplitudes[s], phases[x ^ delta] - phases[x])
         for s, delta in enumerate(displacements)}
        for x in range(SIZE)
    ]


def monomial_tables(recipe):
    """Decode |x> -> i^(q(x)+phase) |Gx xor offset> directly."""
    keys = {"matrix_rows", "offset", "quadratic_rows", "linear_Z4", "phase"}
    require(set(recipe) == keys, "Unknown monomial fields")
    rows, quad, linear = [recipe[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4")]
    require(all(len(v) == N for v in (rows, quad, linear)), "Wrong monomial dimension")
    require(all(type(v) is int and 0 <= v < SIZE for v in rows + quad), "Invalid binary rows")
    require(all(type(v) is int and 0 <= v < 4 for v in linear), "Invalid Z4 coefficient")
    require(type(recipe["offset"]) is int and 0 <= recipe["offset"] < SIZE, "Invalid offset")
    require(type(recipe["phase"]) is int and 0 <= recipe["phase"] < 4, "Invalid phase")
    require(all(((quad[i] >> j) & 1) == ((quad[j] >> i) & 1)
                for i in range(N) for j in range(N)), "Nonsymmetric quadratic form")
    require(all(linear[i] % 2 == ((quad[i] >> i) & 1) for i in range(N)),
            "Quadratic/linear parity mismatch")
    destinations, phases = [], []
    for x in range(SIZE):
        destinations.append(sum(parity(row & x) << i for i, row in enumerate(rows)) ^ recipe["offset"])
        q = sum(linear[i] for i in range(N) if x & (1 << i))
        for i in range(N):
            for j in range(i + 1, N):
                if (x >> i) & (x >> j) & (quad[i] >> j) & 1:
                    q += 2
        phases.append((q + recipe["phase"]) % 4)
    require(len(set(destinations)) == SIZE, "Noninvertible monomial")
    return destinations, phases


def recipe_kernel(recipe):
    width = recipe["rank"]
    require(width == 4, "Wrong residual width")
    right, rq = monomial_tables(recipe["right"])
    left, lq = monomial_tables(recipe["left"])
    coefficients = fourier_numerators(width)
    return [
        {left[right[x] ^ s]: times_i(coefficients[s], rq[x] + lq[right[x] ^ s])
         for s in range(1 << width)}
        for x in range(SIZE)
    ]


def difference(expected, actual):
    columns = [x for x in range(SIZE) if expected[x] != actual[x]]
    if not columns:
        return {"different_columns": 0}
    x = columns[0]
    y = next(y for y in sorted(set(expected[x]) | set(actual[x]))
             if expected[x].get(y, (0, 0)) != actual[x].get(y, (0, 0)))
    return {"different_columns": len(columns), "first_input": x, "first_output": y,
            "expected_numerator": list(expected[x].get(y, (0, 0))),
            "actual_numerator": list(actual[x].get(y, (0, 0))), "denominator": 16}


def sparse_digest(columns):
    return digest([[[y, *a] for y, a in sorted(column.items())] for column in columns])


def read_inputs(root):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, wanted in sources["files"].items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == wanted,
                "Source hash mismatch: " + path)
    spec = json.loads((root / SPEC).read_text())
    unique, providers = {}, {}
    for provider, artifacts in sources["artifacts"].items():
        loaded = {}
        for name, pin in artifacts.items():
            raw = (root / pin["path"]).read_bytes()
            value = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
            sha = digest(value)
            require(sha == pin["canonical_json_sha256"], "Artifact semantic hash mismatch: " + pin["path"])
            require(sha == spec["providers"][provider]["artifact_semantic_sha256"][name],
                    "Artifact differs from selected supplier SPEC: " + pin["path"])
            loaded[name] = value
        word = loaded["CANONICAL-WORD.json.gz"]
        recipes = loaded["RESIDUAL-ADAPTERS.json"]["recipes"]
        require((word["v"], word["h"], word["R"]) == (112, N, 492), "Unexpected supplier geometry")
        require(word["frames"][0] == [] and len(word["frames"][1]) == N, "Unexpected frame sentinels")
        require(len(word["start"]) == len(word["final"]) == 716, "Wrong column count")
        instances = []
        for register in range(224, 716):
            e, u = word["start"][register], word["final"][register]
            if e != 0 or u == 1:
                continue
            frame = word["frames"][u]
            recipe = recipes[f"0:{u}"]
            require((recipe["frame"], recipe["terminal"], recipe["entrance_rank"],
                     recipe["terminal_rank"], recipe["rank"]) == (0, u, 0, 4, 4), "Wrong cold recipe metadata")
            require(recipe["vectors"] == [] and recipe["terminal_vectors"] == frame, "Wrong recipe frame")
            normalized = {k: recipe[k] for k in ("rank", "left", "right")}
            key = tuple(frame)
            if key in unique:
                require(unique[key] == normalized, "Different recipes for a shared cold frame")
            unique[key] = normalized
            instances.append({"register": register, "terminal_frame_id": u, "vectors": frame})
        require(len(instances) == 22, "Unexpected cold helper inventory")
        providers[provider] = instances
    require(len(unique) == 14, "Unexpected unique cold frame count")
    return unique, providers


def audit(root):
    unique, providers = read_inputs(root)
    entries, controls = [], []
    ordered = sorted(unique)
    # Seed chooses the first tested frame; every frame and column is still covered.
    start = SEED % len(ordered)
    ordered = ordered[start:] + ordered[:start]
    for frame in ordered:
        recipe = unique[frame]
        expected = frame_kernel(frame)
        actual = recipe_kernel(recipe)
        require(expected == actual, "Cold wrapper operator mismatch: " + str(frame))
        require(all(len(column) == 16 for column in actual), "Wrong column support")
        entries.append({"frame": list(frame), "columns": SIZE, "matrix_entries": SIZE * SIZE,
                        "nonzero_entries": SIZE * 16, "amplitude_denominator": 16,
                        "kernel_sha256": sparse_digest(actual)})
        mutants = {}
        for side in ("left", "right"):
            bad = copy.deepcopy(recipe)
            bad[side]["phase"] = (bad[side]["phase"] + 1) % 4
            mutants[side + "_global_phase"] = bad
        bad = copy.deepcopy(recipe)
        bad["left"], bad["right"] = bad["right"], bad["left"]
        mutants["swapped_sides"] = bad
        bad = copy.deepcopy(recipe)
        bad["left"]["offset"] ^= 1
        mutants["left_translation"] = bad
        # Right-compose with Z on a seed-selected input coordinate. It fixes |0>
        # and leaves the support/width intact, but negates exactly 256 columns.
        axis = SEED % N
        bad = copy.deepcopy(recipe)
        bad["right"]["linear_Z4"][axis] = (bad["right"]["linear_Z4"][axis] + 2) % 4
        mutants["zero_column_blind_phase"] = bad
        for name, mutant in mutants.items():
            result = recipe_kernel(mutant)
            witness = difference(expected, result)
            require(witness["different_columns"] > 0, "Mutation accepted: " + name)
            if name == "zero_column_blind_phase":
                require(result[0] == expected[0], "Blind control changed |0>")
                require(all(set(a) == set(b) for a, b in zip(expected, result)), "Blind control changed support")
                require(witness["different_columns"] == SIZE // 2, "Wrong phase-column count")
            controls.append({"frame": list(frame), "mutation": name, **witness})
    return {"status": "PASS_COLD_WRAPPER_AMPLITUDE_AUDIT", "seed": SEED,
            "scope": "Exact finite cold-wrapper matrices only; no multiplication theorem or new kappa.",
            "providers": providers, "unique_frames": len(entries), "helper_instances": 44,
            "basis_columns": sum(e["columns"] for e in entries),
            "matrix_entries": sum(e["matrix_entries"] for e in entries),
            "nonzero_entries": sum(e["nonzero_entries"] for e in entries),
            "identities": entries, "negative_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository containing the pinned inputs")
    parser.add_argument("--write", type=Path, help="Write a new receipt; refuses to overwrite")
    args = parser.parse_args()
    result = audit(args.root)
    if args.write:
        with args.write.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        require(result == expected, "Receipt differs from EXPECTED.json")
    print(f"{result['status']}: {result['unique_frames']} frames; {result['helper_instances']} helpers; "
          f"{result['basis_columns']} columns; {result['matrix_entries']} entries; "
          f"{len(result['negative_controls'])} rejected mutations")


if __name__ == "__main__":
    main()
