"""Check every named subfamily of an affine plane in one complete GL_3 census."""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from finite import Field
from headers import census
from laws import full_flat


def superset_sums(values, k):
    """Replace each cell by the sum over masks containing its mask."""
    sums = values[:]
    for bit in range(k):
        half = 1 << bit
        for block in range(0, len(sums), 2*half):
            for i in range(block, block + half):
                sums[i] += sums[i + half]
    return sums


def torus_profile(field, space, forms):
    masks = [0]*(1 << len(forms))
    for vector in space:
        nonzero = sum(1 << i for i, row in enumerate(forms) if field.dot(row, vector))
        masks[nonzero] += 1
    return superset_sums(masks, len(forms))


def one_plane(q):
    f = Field(q)
    forms = [(1, a, b) for a, b in f.vectors(2)]
    k = len(forms)
    matrix = census(q, 3, forms)
    masks = [0]*(1 << k)
    for name, count in matrix["masks"].items():
        masks[int(name)] = count
    actual = superset_sums(masks, k)
    whole = torus_profile(f, f.vectors(3), forms)
    # Explicit q+1 planes through e1, parametrized by quotient projective lines.
    planes = []
    lines = set()
    for u, v in [(1, i) for i in range(q)] + [(0, 1)]:
        coordinates = [(a, f.mul[b][u], f.mul[b][v]) for a, b in f.vectors(2)]
        planes.append(torus_profile(f, coordinates, forms))
        for intercept in range(q):
            line = sum(1 << i for i, (_, a, b) in enumerate(forms)
                       if f.dot((u,v), (a,b)) == intercept)
            sub = line
            while sub:
                lines.add(sub)
                sub = (sub - 1) & line
    # At m=r=3 there is exactly one header per master tuple. All nonempty
    # subsets are evaluated on this SAME rank-three master; even collinear
    # subsets use this denominator, with unconstrained coordinates retained.
    counts = defaultdict(lambda: [0, 0, 0])
    digest = hashlib.sha256()
    a = q + (q - 1)**2
    p_num, p_den = (q - 1)*a*a, (q**3 - 1)*q*q
    for mask, seen in enumerate(actual):
        if mask:
            predicted = (q - 1)*((q**3 + (q - 1)*whole[mask])**2
                        - sum((q*q + (q - 1)*plane[mask])**2 for plane in planes)
                        + q*a*a)
            if predicted != seen:
                raise ValueError(f"affine plane subset q={q}, mask={mask}")
            h = mask.bit_count()
            rank = 1 if h == 1 else (2 if mask in lines else 3)
            delta = seen*p_den**h - matrix["headers"]*p_num**h
            counts[h,rank][1 + (delta > 0) - (delta < 0)] += 1
        digest.update(seen.to_bytes(4, "little"))
    if actual[0] != matrix["headers"] or sum(sum(x) for x in counts.values()) != (1 << k) - 1:
        raise ValueError("plane subset coverage")
    if actual[-1] != matrix["headers"]*full_flat(q, 3, 3):
        raise ValueError("all affine directions vs full-flat specialization")
    return dict(q=q, named_directions=k, headers=matrix["headers"], subsets=1 << k,
                determinant_classes=matrix["determinant_classes"],
                nonempty_mask_signs_by_size_rank={f"{h},{r}":v for (h,r),v in sorted(counts.items())},
                subset_count_sha256=digest.hexdigest(), word_det_mask_sha256=matrix["word_det_mask_sha256"],
                observed_exact_masks=matrix["masks"])


def collect():
    return [one_plane(q) for q in (2, 3, 4)]


if __name__ == "__main__":
    rows = collect()
    if rows != json.loads((HERE/"AFFINE-PLANES.json").read_text(encoding="utf8")):
        raise ValueError("frozen affine-plane census")
    print(json.dumps(dict(status="PASS_COMPLETE_AFFINE_PLANES",headers=sum(x["headers"] for x in rows),
                          subset_counts=sum(x["subsets"] for x in rows), field_orders=[2,3,4])))
