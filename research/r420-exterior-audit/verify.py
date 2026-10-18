#!/usr/bin/env python3
"""Independent finite R420 geometry audit. Sagar Thakrar / OpenAI Codex.

Apache-2.0. Uses no predecessor implementation and no third-party packages.
"""

import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 83
H = 8


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def dyadic(n):
    return n > 0 and n & (n - 1) == 0


def wedge(w, vector):
    """Append one vector; masks label the increasing exterior basis."""
    out = Counter()
    for mask, value in w.items():
        for j, x in enumerate(vector):
            if x and not mask & (1 << j):
                sign = -1 if bin(mask >> (j + 1)).count("1") % 2 else 1
                out[mask | (1 << j)] += sign * value * x
    return {mask: value for mask, value in out.items() if value}


def exterior_basis(lines, indices):
    w = {0: 1}
    selected = []
    content = 1
    for i in indices:
        candidate = wedge(w, lines[i])
        if not candidate:
            continue
        divisor = gcd(*candidate.values())
        content *= divisor
        if candidate[min(candidate)] < 0:
            divisor = -divisor
        w = {mask: value // divisor for mask, value in candidate.items()}
        selected.append(i)
    return w, selected, content


def projector(w):
    contractions = []
    for j in range(H):
        contractions.append({
            mask ^ (1 << j): value * (-1 if bin(mask & ((1 << j) - 1)).count("1") % 2 else 1)
            for mask, value in w.items() if mask & (1 << j)
        })
    norm = sum(value * value for value in w.values())
    numerator = [[sum(value * contractions[j].get(mask, 0)
                      for mask, value in contractions[i].items())
                  for j in range(H)] for i in range(H)]
    divisor = gcd(norm, *(value for row in numerator for value in row))
    return [[value // divisor for value in row] for row in numerator], norm // divisor, norm


def product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(H))
             for j in range(H)] for i in range(H)]


def apply(a, vector):
    return [sum(x * y for x, y in zip(row, vector)) for row in a]


def check_projector(n, d, rank):
    require(dyadic(d), "non-dyadic projector denominator")
    require(all(n[i][j] == n[j][i] for i in range(H) for j in range(H)),
            "projector not symmetric")
    require(product(n, n) == [[d * x for x in row] for row in n],
            "projector not idempotent")
    require(sum(n[i][i] for i in range(H)) == rank * d, "projector trace")


def check_frame(lines, indices):
    require(len(indices) == len(set(indices)) and
            all(type(i) is int and 0 <= i < len(lines) for i in indices),
            "frame line indices")
    ordered = sorted(indices, key=lambda i: (i - SEED) % len(lines))
    w, basis, content = exterior_basis(lines, ordered)
    n, d, norm = projector(w)
    rank = len(basis)
    check_projector(n, d, rank)
    require(dyadic(content) and dyadic(norm), "non-dyadic basis Gram witness")
    inside = []
    residual_contents = Counter()
    for i, line in enumerate(lines):
        residual = [a - d * x for a, x in zip(apply(n, line), line)]
        divisor = gcd(*residual)
        if divisor == 0:
            inside.append(i)
        else:
            require(dyadic(divisor), "root incidence can change at an odd prime")
            residual_contents[str(divisor)] += 1
    require(inside == sorted(indices), "frame not closed")
    # Changing every greedy choice must preserve the primitive exterior line.
    reverse, _, _ = exterior_basis(lines, reversed(ordered))
    require(reverse == w, "exterior coordinates depend on basis order")
    receipt = {"rank": rank, "basis": basis, "basis_content": content,
               "primitive_norm_squared": norm, "projector_denominator": d,
               "exterior": sorted([mask, value] for mask, value in w.items()),
               "nonincident_residual_contents": dict(sorted(residual_contents.items()))}
    return n, d, receipt


def geometry(word):
    require((word["h"], word["v"], word["R"], word["form"]) ==
            (8, 120, 420, "<x,y>/2"), "R420 header")
    lines = word["lines"]
    require(len(lines) == 120 and all(len(line) == H and
            all(type(x) is int for x in line) for line in lines), "label dimensions")
    require(all(sum(x * x for x in line) == 4 for line in lines), "label norm")
    require(all(sum(x * y for x, y in zip(lines[i], lines[j])) in (-2, 0, 2)
                for i in range(120) for j in range(i)), "label inner product")
    frames = [check_frame(lines, indices) for indices in word["frames"]]
    zero = [i for i, (_, _, rec) in enumerate(frames) if rec["rank"] == 0]
    full = [i for i, (_, _, rec) in enumerate(frames) if rec["rank"] == H]
    require(len(zero) == len(full) == 1, "unique zero and full frames")
    return frames, zero[0], full[0]


def check_stream(word, frames, zero, full):
    v, size = 120, 660
    require(len(word["start"]) == len(word["final"]) == size, "endpoint lengths")
    require(all(type(f) is int and 0 <= f < len(frames)
                for f in word["start"] + word["final"]), "endpoint frame index")
    for r, f in enumerate(word["start"]):
        if r < v:
            n, d, rec = frames[f]
            require(rec["rank"] == 1 and apply(n, word["lines"][r]) ==
                    [d * x for x in word["lines"][r]], "source start line")
        else:
            require(f == zero, "non-source start frame")
    for r, f in enumerate(word["final"]):
        if v <= r < 2 * v:
            n, _, rec = frames[f]
            require(rec["rank"] == 7 and apply(n, word["lines"][r - v]) == [0] * H,
                    "target final hyperplane")
        else:
            require(f == full, "source/helper final frame")
    cur = word["start"][:]
    edges = set()
    moves = Counter()

    def move(register, frame, phase):
        old = cur[register]
        if old == frame:
            return
        a, _, ar = frames[old]
        b, bd, br = frames[frame]
        if (old, frame) not in edges:
            require(ar["rank"] < br["rank"] and
                    product(b, a) == [[bd * x for x in row] for row in a],
                    "non-nested frame move")
            edges.add((old, frame))
        moves[phase] += 1
        cur[register] = frame

    retained_ranks = []
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            require(all(cur[r] == zero for r in range(v, 2 * v)), "scatter target frame")
            require(len(word["ret"]) == 9 and len(set(word["ret"])) == 9 and
                    all(type(r) is int and 2 * v <= r < size for r in word["ret"]),
                    "retained helper indices")
            retained_ranks = [frames[cur[r]][2]["rank"] for r in word["ret"]]
            require(retained_ranks == [8] * 9, "retained copy ranks")
            continue
        for f, destination, sources in word[phase]:
            registers = [destination] + sources
            require(type(f) is int and 0 <= f < len(frames), "gate frame index")
            require(len(registers) == len(set(registers)) and
                    all(type(r) is int and 0 <= r < size for r in registers), "gate registers")
            if phase == "D":
                require(f == zero, "D frame")
            for r in registers:
                move(r, f, phase)
    for r, f in enumerate(word["final"]):
        move(r, f, "final")
    return {"moves_by_phase": dict(sorted(moves.items())),
            "distinct_nested_pairs": sorted([a, b] for a, b in edges),
            "retained_copy_ranks": retained_ranks}


def controls(word, frames, zero, full):
    rejected = []

    def reject(name, expected, operation):
        try:
            operation()
        except Rejected as error:
            require(str(error) == expected, "wrong control rejection: " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise Rejected("control accepted: " + name)

    positive = 0
    axes = [[int(i == j) for j in range(H)] for i in range(H)]
    for mask in range(1 << H):
        chosen = [i for i in range(H) if mask & (1 << i)]
        w, _, _ = exterior_basis(axes, chosen)
        n, d, _ = projector(w)
        require(d == 1 and n == [[int(i == j and i in chosen) for j in range(H)]
                                for i in range(H)], "coordinate-subspace oracle")
        positive += 1
    oblique = [[1, 1, 0, 0, 0, 0, 0, 0]]
    w, _, _ = exterior_basis(oblique, [0])
    n, d, _ = projector(w)
    require(d == 2 and n == [[int(i < 2 and j < 2) for j in range(H)]
                            for i in range(H)], "oblique-line oracle")
    positive += 1
    mixed = [[1, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 1, 0, 0, 0, 0]]
    w, _, _ = exterior_basis(mixed, [0, 1])
    mixed_n, mixed_d, norm = projector(w)
    require(w == {3: 1, 9: 1, 6: -1, 12: 1} and norm == 4 and mixed_d == 2 and
            mixed_n == [[int(i < 4 and j < 4 and i % 2 == j % 2)
                         for j in range(H)] for i in range(H)], "mixed-sign plane oracle")
    positive += 1
    corrupt = copy.deepcopy(n)
    corrupt[0][0] += 1
    reject("corrupted projector", "projector not idempotent", lambda: check_projector(corrupt, d, 1))
    w, _, _ = exterior_basis([[1, 1, 1, 0, 0, 0, 0, 0]], [0])
    bad_n, bad_d, _ = projector(w)
    require(bad_d == 3, "prime-three control denominator")
    reject("rational line singular at prime 3", "non-dyadic projector denominator",
           lambda: check_projector(bad_n, bad_d, 1))
    a2 = [0, 16, 23]
    w, _, _ = exterior_basis(word["lines"], a2)
    a2_n, a2_d, a2_norm = projector(w)
    require(a2_norm == a2_d == 3 and
            [i for i, line in enumerate(word["lines"]) if apply(a2_n, line) ==
             [a2_d * x for x in line]] == a2, "closed A2 control")
    reject("closed A2 frame singular at prime 3", "non-dyadic projector denominator",
           lambda: check_frame(word["lines"], a2))
    bad_n, bad_d, _ = projector({3: 1, 12: 1})
    reject("nondecomposable exterior two-vector", "projector not idempotent",
           lambda: check_projector(bad_n, bad_d, 2))
    reject("odd-index basis with integral projector", "non-dyadic basis Gram witness",
           lambda: check_frame([[3, 0, 0, 0, 0, 0, 0, 0]], [0]))
    reject("extra incidence after reduction modulo 3", "root incidence can change at an odd prime",
           lambda: check_frame([[1, 0, 0, 0, 0, 0, 0, 0],
                                [1, 3, 0, 0, 0, 0, 0, 0]], [0]))
    reject("omitted line from full frame", "frame not closed",
           lambda: check_frame(word["lines"], word["frames"][full][1:]))
    reject("duplicate line", "frame line indices",
           lambda: check_frame(word["lines"], [0, 0]))
    changed = copy.deepcopy(word)
    changed["final"][120] = word["final"][121]
    reject("wrong target hyperplane", "target final hyperplane",
           lambda: check_stream(changed, frames, zero, full))
    changed = copy.deepcopy(word)
    changed["B"][0][0] = zero
    reject("phase-B descent to zero", "non-nested frame move",
           lambda: check_stream(changed, frames, zero, full))
    changed = copy.deepcopy(word)
    changed["D"][0][0] = full
    reject("D moved off zero", "D frame", lambda: check_stream(changed, frames, zero, full))
    return {"positive_oracles": positive, "rejected": rejected}


def certificate():
    source = json.loads((HERE / "SOURCE.json").read_text())
    for name, digest in source["reference_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "reference source drift: " + name)
    payload = gzip.decompress((ROOT / source["word"]).read_bytes())
    require(hashlib.sha256(payload).hexdigest() == source["word_payload_sha256"], "word payload drift")
    word = json.loads(payload)
    frames, zero, full = geometry(word)
    stream = check_stream(word, frames, zero, full)
    return {"status": "PASS_R420_EXTERIOR_GEOMETRY", "seed": SEED,
            "word_payload_sha256": source["word_payload_sha256"],
            "frame_count": len(frames),
            "rank_histogram": dict(sorted(Counter(str(rec["rank"]) for _, _, rec in frames).items())),
            "denominator_histogram": dict(sorted(Counter(str(d) for _, d, _ in frames).items())),
            "nonincident_pairs": sum(sum(rec["nonincident_residual_contents"].values())
                                     for _, _, rec in frames),
            "frames": [rec for _, _, rec in frames],
            "stream": stream, "controls": controls(word, frames, zero, full)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the regenerated certificate to stdout")
    args = parser.parse_args()
    result = certificate()
    if args.emit:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
        print(result["status"] + ": " + str(result["frame_count"]) + " frames; " +
              str(len(result["stream"]["distinct_nested_pairs"])) + " nested pairs; " +
              str(result["controls"]["positive_oracles"]) + " positive oracles; " +
              str(len(result["controls"]["rejected"])) + " rejected controls")


if __name__ == "__main__":
    main()
