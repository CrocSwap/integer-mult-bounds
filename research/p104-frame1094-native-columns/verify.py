#!/usr/bin/env python3
"""Exact independent width1 operator check of the four new-frame1094 tasks.

The expected operator uses a closed canonical-frame kernel and finite Gaussian
convolution. No producer, compiler, author native checker, or oracle is imported.
"""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED = {
    "sources/NOTICE": [
        "6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd",
        "e6cae17f778e8e31b7c294ff2890c545978931c0"
    ],
    "sources/WORD.json.gz": [
        "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928",
        "03ea7690285d4cda72815f962d5710ab96e08490"
    ],
    "sources/clifford_exact.py": [
        "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
        "166841a037f069249f6f7f6dedb89248812f59e2"
    ],
    "sources/integration-source.py": [
        "7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597",
        "b7be846b10c4c54a4e1558d7b563bc8c3a170223"
    ],
    "sources/native-channel-PROOF.md": [
        "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c",
        "a69311b74f74a2f8e8f411c1451baacd9bacddce"
    ]
}
RECIPES_SHA256 = "b33e9ad1eb25daf857d144ac75bb09ea60b2d6eb5a22605e78e71999491b9335"
CASES = [
    ("move-712-1094", "move", 712, 1094, [703], [12917]),
    ("move-714-1094", "move", 714, 1094, [704], [12930]),
    ("move-1094-127", "move", 1094, 127, [704], [12932]),
    ("helper-3-1094", "helper", 3, 1094, [703], []),
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    authenticated = {}
    for filename, (digest, blob) in PINNED.items():
        raw = (HERE / filename).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + filename)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + filename)
        authenticated[filename] = raw
    return authenticated


def rotate(pair, phase):
    real, imaginary = pair
    return ((real, imaginary), (-imaginary, real), (-real, -imaginary), (imaginary, -real))[phase % 4]


def gaussian_product(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def points(vectors):
    result = [0]
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512 and vector not in result,
                "independent nine-axis frame basis")
        result += [value ^ vector for value in tuple(result)]
    return result


def coefficients(rank):
    base = (1, 0)
    for _ in range(rank):
        base = gaussian_product(base, (1, 1))
    return [rotate(base, -mask.bit_count()) for mask in range(1 << rank)]


def frame_kernel(vectors):
    rank = len(vectors)
    require(rank <= 9, "frame rank at most nine")
    shifts = points(vectors)
    if rank == 0:
        return {"rank": 0, "shifts": [0], "phases": [0] * 512, "coefficients": [(1, 0)]}
    if rank == 9:
        # The frozen definition uses F9 directly, regardless of the supplied basis.
        return {"rank": 9, "shifts": list(range(512)), "phases": [0] * 512,
                "coefficients": coefficients(9)}
    # Enumerating all512 coordinates independently supplies the binary inverse.
    complete = list(shifts)
    for axis in range(9):
        vector = 1 << axis
        if vector not in complete:
            complete += [value ^ vector for value in tuple(complete)]
    require(len(complete) == 512 and len(set(complete)) == 512, "complete binary chart")
    inverse = [0] * 512
    for coordinate, address in enumerate(complete):
        inverse[address] = coordinate
    columns = [inverse[1 << axis] for axis in range(9)]
    phases = []
    for address in range(512):
        active = [axis for axis in range(9) if address >> axis & 1]
        phase = sum(1 ^ (columns[axis].bit_count() % 2) for axis in active)
        phase += 2 * sum((columns[a] & columns[b]).bit_count() % 2
                         for index, a in enumerate(active) for b in active[index + 1:])
        phases.append(phase % 4)
    return {"rank": rank, "shifts": shifts, "phases": phases, "coefficients": coefficients(rank)}


def frame_column(frame, address, adjoint=False):
    phase = frame["phases"][address]
    result = {}
    for shift, coefficient in zip(frame["shifts"], frame["coefficients"]):
        target = address ^ shift
        if adjoint:
            coefficient = (coefficient[0], -coefficient[1])
        result[target] = rotate(coefficient, frame["phases"][target] - phase)
    return result


def transport_column(source, target, address):
    """Compute Gamma_target Gamma_source^dagger on one basis column."""
    result = {}
    phases = target["phases"]
    flat_phase = not any(phases)
    for middle, first in frame_column(source, address, True).items():
        initial_phase = phases[middle]
        for shift, coefficient in zip(target["shifts"], target["coefficients"]):
            output = middle ^ shift
            if not flat_phase:
                coefficient = rotate(coefficient, phases[output] - initial_phase)
            real = first[0] * coefficient[0] - first[1] * coefficient[1]
            imaginary = first[0] * coefficient[1] + first[1] * coefficient[0]
            if output in result:
                result[output][0] += real
                result[output][1] += imaginary
            else:
                result[output] = [real, imaginary]
    return normalize(result, source["rank"] + target["rank"])


def normalize(state, exponent):
    state = {address: (pair[0], pair[1]) for address, pair in state.items() if pair[0] or pair[1]}
    require(state and type(exponent) is int and exponent >= 0, "nonzero dyadic Gaussian column")
    while exponent and all((pair[0] | pair[1]) % 2 == 0 for pair in state.values()):
        state = {address: (pair[0] // 2, pair[1] // 2) for address, pair in state.items()}
        exponent -= 1
    return state, exponent


def monomial(record):
    require(type(record) is dict and set(record) ==
            {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"}, "monomial fields")
    matrix, quadratic, linear = record["matrix_rows"], record["quadratic_rows"], record["linear_Z4"]
    require(all(type(row) is list and len(row) == 9 for row in (matrix, quadratic, linear)), "monomial dimension")
    require(all(type(x) is int and 0 <= x < 512 for x in matrix + quadratic), "binary monomial entries")
    require(all(type(x) is int and 0 <= x < 4 for x in linear), "Z4 monomial entries")
    require(type(record["offset"]) is int and 0 <= record["offset"] < 512 and
            type(record["phase"]) is int and 0 <= record["phase"] < 4, "monomial shift and phase")
    require(all(((quadratic[i] >> j) & 1) == ((quadratic[j] >> i) & 1)
                for i in range(9) for j in range(9)), "symmetric quadratic form")
    require(all(linear[i] % 2 == ((quadratic[i] >> i) & 1) for i in range(9)), "quadratic diagonal parity")
    permutation, phases = [], []
    for address in range(512):
        output = sum(((row & address).bit_count() % 2) << i for i, row in enumerate(matrix))
        permutation.append(output ^ record["offset"])
        active = [i for i in range(9) if address >> i & 1]
        phase = record["phase"] + sum(linear[i] for i in active)
        phase += 2 * sum((quadratic[i] >> j) & 1 for index, i in enumerate(active) for j in active[index + 1:])
        phases.append(phase % 4)
    require(len(set(permutation)) == 512, "invertible monomial permutation")
    return permutation, phases


def prepared_recipe(record, expected_rank):
    require(type(record) is dict and set(record) == {"rank", "left", "right"}, "native recipe fields")
    require(type(record["rank"]) is int and record["rank"] == expected_rank, "declared native rank")
    left = monomial(record["left"])
    if expected_rank == 0:
        require(record["right"] is None, "rank-zero right factor")
        right = None
    else:
        right = monomial(record["right"])
    return {"rank": expected_rank, "left": left, "right": right, "coefficients": coefficients(expected_rank)}


def recipe_column(recipe, address):
    left_permutation, left_phase = recipe["left"]
    if recipe["right"] is None:
        return normalize({left_permutation[address]: rotate((1, 0), left_phase[address])}, 0)
    right_permutation, right_phase = recipe["right"]
    middle = right_permutation[address]
    state = {}
    for mask, coefficient in enumerate(recipe["coefficients"]):
        shifted = middle ^ mask
        output = left_permutation[shifted]
        require(output not in state, "distinct native child outputs")
        state[output] = rotate(coefficient, right_phase[address] + left_phase[shifted])
    return normalize(state, recipe["rank"])


def update_digest(digest, address, column):
    state, exponent = column
    row = {"input": address, "denominator_exponent": exponent,
           "entries": [[output, *state[output]] for output in sorted(state)]}
    digest.update((canonical(row) + "\n").encode())


def difference(expected, actual, address):
    left, a = expected
    right, b = actual
    exponent = max(a, b)
    for output in sorted(left.keys() | right.keys()):
        x, y = left.get(output, (0, 0)), right.get(output, (0, 0))
        if (x[0] << (exponent - a), x[1] << (exponent - a)) != (y[0] << (exponent - b), y[1] << (exponent - b)):
            return {"input": address, "output": output,
                    "expected": {"real": x[0], "imaginary": x[1], "denominator_exponent": a},
                    "actual": {"real": y[0], "imaginary": y[1], "denominator_exponent": b}}
    return None


def check_task(task, frames):
    a, b = task["source_frame"], task["target_frame"]
    source, target = frame_kernel(frames[a]), frame_kernel(frames[b])
    rank = abs(source["rank"] - target["rank"])
    recipe = prepared_recipe(task["recipe"], rank)
    digest = sha256()
    first_columns = {}
    nonzero = 0
    for address in range(512):
        expected = transport_column(source, target, address)
        actual = recipe_column(recipe, address)
        require(expected == actual, "complete native operator column: " + task["id"] + " input " + str(address))
        update_digest(digest, address, actual)
        nonzero += len(actual[0])
        if address in (0, 1):
            first_columns[address] = expected
    bad = deepcopy(task["recipe"])
    bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    phase_column = recipe_column(prepared_recipe(bad, rank), 0)
    phase_witness = difference(first_columns[0], phase_column, 0)
    require(phase_witness is not None, "global phase control rejected")
    bad = deepcopy(task["recipe"])
    bad["right"]["linear_Z4"][0] = (bad["right"]["linear_Z4"][0] + 2) % 4
    fault = prepared_recipe(bad, rank)
    require(recipe_column(fault, 0) == first_columns[0], "phase fault preserves entire column zero")
    hidden_witness = difference(first_columns[1], recipe_column(fault, 1), 1)
    require(hidden_witness is not None, "off-zero-column phase control rejected")
    bad = deepcopy(task["recipe"])
    bad["rank"] = rank + 1
    try:
        prepared_recipe(bad, rank)
    except ValueError as error:
        rank_control = str(error)
    else:
        raise ValueError("wrong rank control accepted")
    return {"id": task["id"], "source_frame": a, "target_frame": b, "rank": rank,
            "columns": 512, "coefficient_slots": 512 * 512, "nonzero_coefficients": nonzero,
            "matrix_sha256": digest.hexdigest(),
            "controls": {"global_i_phase": phase_witness,
                         "column_zero_preserving_phase": hidden_witness,
                         "wrong_rank_rejected": rank_control}}


def run():
    authenticated = authenticate()
    word = json.loads(gzip.decompress(authenticated["sources/WORD.json.gz"]))
    retained = HERE / "RECIPES.json"
    require(retained.is_file(), "retained RECIPES.json receipt must exist")
    records = json.loads(retained.read_bytes())
    payload = (canonical(records) + "\n").encode()
    require(sha256(payload).hexdigest() == RECIPES_SHA256, "frozen canonical recipe payload")
    require(records["word_sha256"] == PINNED["sources/WORD.json.gz"][0] and
            records["compiler_sha256"] == PINNED["sources/clifford_exact.py"][0], "recipe source bindings")
    frames = word["frames"]
    new_span = set(points(frames[1094]))
    equivalence = {"basis": frames[1094], "rank": len(frames[1094]),
                   "older_exact_basis_matches": [i for i, frame in enumerate(frames[:1094]) if frame == frames[1094]],
                   "older_span_matches": [i for i, frame in enumerate(frames[:1094]) if set(points(frame)) == new_span]}
    require(records["frame1094"] == equivalence, "independent historical frame comparison")
    require(len(records["tasks"]) == len(CASES), "four-task coverage")
    for task, (label, kind, a, b, roles, indices) in zip(records["tasks"], CASES):
        require({key: task[key] for key in ("id", "kind", "source_frame", "target_frame", "roles", "event_indices")} ==
                {"id": label, "kind": kind, "source_frame": a, "target_frame": b,
                 "roles": roles, "event_indices": indices}, "literal task binding")
        for index, role in zip(indices, roles):
            require(word["program"][index] == ["MOVE", role, a, b, False], "actual paid MOVE binding")
        if kind == "helper":
            require(word["initial"][703] == a and word["final"][703] == b, "actual helper normalizer binding")
    results = [check_task(task, frames) for task in records["tasks"]]
    return {"schema_version": 1, "scope": "four new-frame1094 native operators at tensor width1",
            "recipes_canonical_sha256": RECIPES_SHA256, "frame1094": equivalence,
            "maps": results, "columns": 4 * 512, "coefficient_slots": 4 * 512 * 512,
            "nonzero_coefficients": sum(task["nonzero_coefficients"] for task in results),
            "limits": ["The declared canonical chart and primitive C semantics are the operator specification.",
                       "Historical maps, native tensor widths above1, complete caller and ordinary work are not audited.",
                       "This does not admit erasure, compiler, precision tape, analytic recovery or a new kappa."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh JSON without retained-result comparison")
    options = parser.parse_args()
    result = run()
    if not options.emit:
        retained = HERE / "RESULT.json"
        require(retained.is_file(), "retained RESULT.json receipt must exist")
        require(canonical(json.loads(retained.read_bytes())) == canonical(result), "exact typed retained RESULT.json receipt")
    print(json.dumps(result, sort_keys=True, indent=2))
