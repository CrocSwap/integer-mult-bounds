#!/usr/bin/env python3
"""Independent transpose-circuit and exact GF(2) rank certificate. Apache-2.0.

Joshua Snider, with substantial OpenAI Codex assistance. No supplier imports.
Bit j of an integer represents coordinate j; all arithmetic here is over F2.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED, V, R, N = 80, 120, 420, 660
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_word(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, pin in pins["files"].items():
        data = (root / path).read_bytes()
        # The immutable archive hash is recorded, but proof equality uses payload.
        if path == WORD:
            data = gzip.decompress(data)
            expected = pin["payload_sha256"]
        else:
            expected = pin["sha256"]
        need(digest(data) == expected, "source pin: " + path)
    return json.loads(gzip.decompress((root / WORD).read_bytes()))


def stream(w, sections=("A", "scatter", "B")):
    need((w["v"], w["R"], w["h"]) == (V, R, 8), "word dimensions")
    need(w["format"] == "bitE8/1+mut", "word format")
    gates = []
    for section in sections:
        if section == "scatter":
            need(len(w["scatter"]) == V, "scatter length")
            need(all(240 <= q < N for q in w["ret"]), "retained helper")
            for t, indices in enumerate(w["scatter"]):
                need(all(0 <= k < len(w["ret"]) for k in indices), "scatter index")
                gates.append((V + t, tuple(w["ret"][k] for k in indices)))
        else:
            for frame, dest, sources in w[section]:
                need(0 <= frame < len(w["frames"]), "frame index")
                gates.append((dest, tuple(sources)))
    for dest, sources in gates:
        need(0 <= dest < N and all(0 <= s < N for s in sources), "register index")
        need(dest not in sources and len(set(sources)) == len(sources), "transvection operands")
    return gates


def pullback(gates, outputs):
    """Pull output covectors backward; never propagates register expressions."""
    columns = [0] * N
    for bit, register in enumerate(outputs):
        columns[register] = 1 << bit
    for dest, sources in reversed(gates):
        weight = columns[dest]
        for source in sources:
            columns[source] ^= weight
    return columns


def literal_d(w):
    cols = [0] * R
    for frame, dest, sources in w["D"]:
        need(not w["frames"][frame], "D frame is not zero")
        need(V <= dest < 2 * V, "D target")
        for source in sources:
            need(2 * V <= source < N, "D helper")
            cols[source - 2 * V] ^= 1 << (dest - V)
    return cols


def extract(w):
    cols = pullback(stream(w), range(V, 2 * V))
    need(cols[:V] == [1 << j for j in range(V)], "source block J differs from I")
    need(cols[V:2 * V] == [1 << j for j in range(V)], "target block V differs from I")
    need(cols[2 * V:] == literal_d(w), "dirty block K differs from D")
    return cols[2 * V:]


def apply_columns(columns, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return out


def apply_rows(rows, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(rows))


def transpose(columns, height):
    return [sum(((c >> i) & 1) << j for j, c in enumerate(columns)) for i in range(height)]


def nominate_columns(columns):
    """Discovery only: the returned minor is subsequently checked by products."""
    basis, chosen = {}, []
    for j in list(range(SEED, R)) + list(range(SEED)):
        value = columns[j]
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                chosen.append(j)
                break
        if len(chosen) == V:
            return chosen
    raise Reject("no full-rank minor found")


def inverse(rows):
    n = len(rows)
    work = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        pivot = next((k for k in range(j, n) if (work[k] >> j) & 1), None)
        need(pivot is not None, "singular minor")
        work[j], work[pivot] = work[pivot], work[j]
        for k in range(n):
            if k != j and ((work[k] >> j) & 1):
                work[k] ^= work[j]
    need([x & ((1 << n) - 1) for x in work] == [1 << i for i in range(n)], "inverse elimination")
    return [x >> n for x in work]


def check_certificate(columns, pivots, inv, kernel):
    need(len(columns) == R and all(0 <= c < (1 << V) for c in columns), "K dimensions")
    need(len(pivots) == V and len(set(pivots)) == V and all(0 <= p < R for p in pivots), "pivot indices")
    need(len(inv) == V and all(0 <= r < (1 << V) for r in inv), "inverse dimensions")
    minor = [columns[p] for p in pivots]
    right = []
    for t in range(V):
        coefficients = apply_rows(inv, 1 << t)
        need(apply_columns(minor, coefficients) == 1 << t, "M inverse product")
        need(apply_rows(inv, minor[t]) == 1 << t, "inverse M product")
        right.append(sum(((coefficients >> j) & 1) << p for j, p in enumerate(pivots)))
    free = [j for j in range(R) if j not in set(pivots)]
    need(len(kernel) == R - V, "kernel count")
    for f, vector in zip(free, kernel):
        need(0 <= vector < (1 << R), "kernel dimensions")
        need(apply_columns(columns, vector) == 0, "kernel annihilation")
        need([j for j in free if (vector >> j) & 1] == [f], "kernel free-coordinate identity")
    return right


def distance_four(columns):
    """Exhaust weight <= 3 via column equality/XOR; exhibit weight four."""
    need(all(columns), "weight-one kernel vector")
    need(len(set(columns)) == len(columns), "weight-two kernel vector")
    lookup = set(columns)
    pairs, quads = {}, set()
    count = 0
    for a in range(len(columns)):
        for b in range(a + 1, len(columns)):
            count += 1
            value = columns[a] ^ columns[b]
            need(value not in lookup, "weight-three kernel vector")
            for c, d in pairs.get(value, []):
                need(len({a, b, c, d}) == 4, "overlapping equal pairs")
                quads.add(tuple(sorted((a, b, c, d))))
            pairs.setdefault(value, []).append((a, b))
    need(quads, "no weight-four witness")
    # Every weight-four word is encountered through its three pair partitions.
    ordered = sorted(quads)
    witness = ordered[SEED % len(ordered)]
    need(apply_columns(columns, sum(1 << j for j in witness)) == 0, "weight-four witness")
    return {"minimum_weight": 4, "pairs_checked": count,
            "weight_four_words": len(ordered),
            "weight_four_supports_absolute": [[j + 240 for j in q] for q in ordered],
            "selected_weight_four_helpers_absolute": [j + 240 for j in witness]}


def rejects(action, expected):
    try:
        action()
    except Reject as error:
        need(str(error) == expected, "wrong rejection: " + str(error))
        return expected
    raise Reject("control accepted: " + expected)


def controls(w, columns, pivots, inv, kernel, right):
    result = {}
    broken = copy.deepcopy(w)
    broken["D"] = []
    result["omit_D"] = rejects(lambda: extract(broken), "dirty block K differs from D")
    broken = copy.deepcopy(w)
    broken["D"][SEED][2].pop()
    result["omit_one_D_operand"] = rejects(lambda: extract(broken), "dirty block K differs from D")
    broken = copy.deepcopy(w)
    broken["D"][SEED][2], broken["D"][SEED + 1][2] = broken["D"][SEED + 1][2], broken["D"][SEED][2]
    # This mutation preserves full rank. Rank alone does not establish K=D.
    wrong_columns = literal_d(broken)
    wrong_pivots = nominate_columns(wrong_columns)
    inverse(transpose([wrong_columns[p] for p in wrong_pivots], V))
    result["swap_D_rows_preserves_rank"] = rejects(lambda: extract(broken), "dirty block K differs from D")
    # A backward pull in forward gate order is not the adjoint of the stream.
    wrong = pullback(list(reversed(stream(w))), range(V, 2 * V))
    need(wrong[2 * V:] != columns, "wrong traversal escaped")
    result["wrong_traversal"] = "different dirty map"
    wrong_inv = inv[:]
    wrong_inv[SEED] ^= 1
    result["corrupt_inverse"] = rejects(lambda: check_certificate(columns, pivots, wrong_inv, kernel), "M inverse product")
    wrong_kernel = kernel[:]
    wrong_kernel[SEED] ^= 1 << pivots[0]
    result["corrupt_kernel"] = rejects(lambda: check_certificate(columns, pivots, inv, wrong_kernel), "kernel annihilation")
    wrong_kernel = kernel[:]
    wrong_kernel[SEED] = wrong_kernel[SEED + 1]
    result["dependent_kernel_basis"] = rejects(lambda: check_certificate(columns, pivots, inv, wrong_kernel), "kernel free-coordinate identity")
    # Omitting all D is invisible on clean helpers, but these 120 witnesses
    # independently isolate each target error, one for each basis direction.
    need(apply_columns(columns, 0) == 0, "clean-helper control")
    isolated = [apply_columns(columns, s) for s in right]
    need(isolated == [1 << t for t in range(V)], "isolated dirty witnesses")
    result["omitted_D_dirty_witnesses"] = len(isolated)
    for name, value, reason in (
        ("zero_column", 0, "weight-one kernel vector"),
        ("duplicate_column", columns[SEED + 1], "weight-two kernel vector"),
        ("three_column_dependency", columns[SEED + 1] ^ columns[SEED + 2], "weight-three kernel vector"),
    ):
        wrong = columns[:]
        wrong[SEED] = value
        result[name] = rejects(lambda: distance_four(wrong), reason)
    return result


def build(w):
    columns = extract(w)
    pivots = nominate_columns(columns)
    inv = inverse(transpose([columns[p] for p in pivots], V))
    free = [j for j in range(R) if j not in set(pivots)]
    kernel = []
    for f in free:
        coefficients = apply_rows(inv, columns[f])
        kernel.append((1 << f) | sum(((coefficients >> j) & 1) << p for j, p in enumerate(pivots)))
    right = check_certificate(columns, pivots, inv, kernel)
    # A second transpose pull checks the complete scalar endpoint, including
    # cleanup and every arbitrary helper/source/target input.
    full = pullback(stream(w, ("D", "A", "scatter", "B", "C")), range(N))
    expected = [(1 << j) ^ ((1 << (V + j)) if j < V else 0) for j in range(N)]
    need(full == expected, "complete scalar endpoint")
    fmt = lambda values: [hex(x) for x in values]
    return {
        "schema": "r420-dirty-rank/1", "seed": SEED,
        "rank": V, "nullity": R - V, "raw_gates": len(stream(w)),
        "raw_binary_additions": sum(len(s) for _, s in stream(w)),
        "K_rows_hex": fmt(transpose(columns, V)),
        "pivot_helpers_absolute": [p + 2 * V for p in pivots],
        "minor_inverse_rows_hex": fmt(inv),
        "kernel_free_helpers_absolute": [f + 2 * V for f in free],
        "kernel_basis_sha256": digest(canonical(fmt(kernel))),
        "right_inverse_columns_sha256": digest(canonical(fmt(right))),
        "isolated_target_80_dirty_input_hex": hex(right[SEED]),
        "kernel_distance": distance_four(columns),
        "complete_endpoint_columns": len(full),
        "controls": controls(w, columns, pivots, inv, kernel, right),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new certificate; refuses overwrite")
    parser.add_argument("--check", type=Path, default=HERE / "EXPECTED.json")
    args = parser.parse_args()
    result = build(load_word())
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        need(result == json.loads(args.check.read_text()), "certificate mismatch")
    print("PASS_R420_DIRTY_RANK rank=120 nullity=300 distance=4 pairs=87990 isolated_errors=120 controls=10")


if __name__ == "__main__":
    main()
