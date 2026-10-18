"""Labels/duals survivor census using low-pivot span reduction.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
Imports no primary census or Euclidean reconstruction implementation.
"""
from collections import Counter
import hashlib


def basis(values):
    pivots = {}
    for vector in values:
        while vector:
            bit = (vector & -vector).bit_length()-1
            if bit in pivots:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    return tuple(pivots[k] for k in sorted(pivots))


def pairing(left, right):
    rows = [sum(((a & b).bit_count() % 2) << j for j, b in enumerate(right)) for a in left]
    return len(basis(rows))


def census(data):
    x, labels, duals = data["X"], data["labels"], data["duals"]
    if len(x) != 112 or len(basis(labels)) != 9 or len(basis(duals)) != 9:
        raise ValueError("independent label span")
    b = [[(a & c).bit_count() % 2 for c in duals] for a in labels]
    if any(b[i][i] != 1 or b[i][j] != b[j][i] for i in range(112) for j in range(112)):
        raise ValueError("independent symmetric form")
    normals = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2)]
    supports = [tuple(i for i, r in enumerate(x) if a*r[4]+c*r[6] != 0) for a, c in normals]
    indices = [[tuple(i for i in s if b[i][j]) for j in range(112)] for s in supports]
    left = [[basis(labels[i] for i in selected) for selected in slots] for slots in indices]
    right = [[basis(duals[i] for i in selected) for selected in slots] for slots in indices]
    zero_pairs = [(i, j) for i in range(112) for j in range(112) if not b[i][j]]
    transcript, histograms, minima, witnesses = bytearray(), [], [], []
    for a in range(5):
        minimum_row = []
        for c in range(5):
            counts, best, witness = Counter(), 10, None
            for i, j in zero_pairs:
                cost = pairing(left[a][j], right[c][i])
                transcript.append(cost)
                counts[cost] += 1
                if cost < best:
                    best, witness = cost, [i, j]
            minimum_row.append(best)
            histograms.append({"left": a, "right": c,
                               "counts": {str(k): v for k, v in sorted(counts.items())}})
            witnesses.append({"left": a, "right": c, "ports": witness, "rank": best})
        minima.append(minimum_row)
    report = {"records": len(transcript), "zero_pairs": len(zero_pairs),
            "support_sizes": list(map(len, supports)), "minima": minima,
            "histograms": histograms, "witnesses": witnesses,
            "transcript_sha256": hashlib.sha256(transcript).hexdigest(),
            "slice_dimensions": [{str(k): v for k, v in sorted(Counter(map(len, slots)).items())}
                                 for slots in left]}
    return report, bytes(transcript)
