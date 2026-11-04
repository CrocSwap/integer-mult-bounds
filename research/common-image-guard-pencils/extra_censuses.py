"""Optional larger counts of the five-direction crossing and ternary quartets."""
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dependency import joint
from finite import Field
from headers import census, check_expected, eliminate
from laws import pencil


def odd_pencil():
    row = census(5, 3, [(1, a) for a in range(5)])
    check_expected(row, lambda mask: pencil(5, mask.bit_count(), 3))
    if row["headers"] != 1488000 or row["masks"]["31"] != 99200:
        raise ValueError("five-direction GL3(F5) census")
    return dict(headers=row["headers"], all_five_pass=row["masks"]["31"],
                masks=row["masks"], word_det_mask_sha256=row["word_det_mask_sha256"])


def ternary_quartets():
    field = Field(3)
    rows = [(1,0,0,0),(1,1,0,0),(1,2,0,0),(1,0,1,0),(1,1,1,0),(1,0,0,1)]
    # Use u=(1,1,1,1), not a coordinate vector. This basis change preserves
    # Vu=t and recovers the indicated dependency forms for comparison.
    forms = [((1-a-b-c) % 3, a, b, c) for _, a, b, c in rows]
    bad = {v: sum(1 << i for i, row in enumerate(forms) if field.dot(row, v) == 1)
           for v in field.vectors(4)}
    points = [v for v in field.vectors(4) if next((x for x in v if x), 0) == 1]
    histogram = Counter()
    for g in product(points, repeat=4):
        det, inv = eliminate(field, g, inverse=True)
        if not det:
            continue
        prefix, passing = (0, 0, 0, 0), 63
        for j in range(3):
            scalar = sum(g[j]) % 3
            prefix = tuple((prefix[i] + scalar*inv[i][j]) % 3 for i in range(4))
            passing &= ~bad[prefix]
        # Each invertible representative stands for 2^4 left row scalings
        # with identical principal minors in every conjugate.
        histogram[passing] += 16
    total = sum(histogram.values())
    if total != 24261120:
        raise ValueError("ternary GL4 cardinality")
    counts = []
    for mask in range(64):
        observed = sum(n for key, n in histogram.items() if key & mask == mask)
        chosen = [v for i, v in enumerate(rows) if mask & (1 << i)]
        if Fraction(observed, total) != joint(field, chosen, 4):
            raise ValueError("ternary projective header subset")
        counts.append(observed)
    return dict(headers=total, representatives=total//16, named_subset_counts=counts,
                quartet_counts=[counts[s] for s in (15, 27, 43)])


def check_retained():
    data = json.loads((HERE/"EXTRA-CENSUSES.json").read_text(encoding="utf8"))
    odd, ternary = data["five_direction_GL3_F5"], data["ternary_GL4"]
    if odd["headers"] != 1488000 or odd["all_five_pass"] != 99200:
        raise ValueError("retained five-direction census")
    check_expected(dict(odd, forms=[(1, a) for a in range(5)], q=5, m=3),
                   lambda mask: pencil(5, mask.bit_count(), 3))
    forms = [(1,0,0,0),(1,1,0,0),(1,2,0,0),(1,0,1,0),(1,1,1,0),(1,0,0,1)]
    counts = ternary["named_subset_counts"]
    if (ternary["headers"], ternary["representatives"], len(counts)) != (24261120, 1516320, 64):
        raise ValueError("retained projective census size")
    if ternary["quartet_counts"] != [counts[i] for i in (15, 27, 43)]:
        raise ValueError("retained quartet labels")
    field = Field(3)
    for mask, count in enumerate(counts):
        chosen = [v for i, v in enumerate(forms) if mask & (1 << i)]
        if count != ternary["headers"]*joint(field, chosen, 4):
            raise ValueError("retained projective census probability")


def main():
    data = dict(five_direction_GL3_F5=odd_pencil(), ternary_GL4=ternary_quartets())
    if data != json.loads((HERE/"EXTRA-CENSUSES.json").read_text(encoding="utf8")):
        raise ValueError("optional complete-header fixtures")
    print(json.dumps(dict(status="PASS_EXTRA_GUARD_CENSUSES",
                          literal_F5_headers=data["five_direction_GL3_F5"]["headers"],
                          F3_representatives=data["ternary_GL4"]["representatives"])))


if __name__ == "__main__":
    main()
