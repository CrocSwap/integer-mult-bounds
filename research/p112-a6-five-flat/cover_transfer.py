"""Construct and exhaustively check the affine four-cube cover transfer."""

from collections import Counter

from vendor.geometry import require

ALL = (1 << 16) - 1


def cover(mask):
    """Return an affine hyperplane mask and at most four uncovered points."""
    require(type(mask) is int and 0 <= mask <= ALL, "four-cube support mask")
    require(mask.bit_count() <= 12, "support exceeds twelve points")
    absent = tuple(x for x in range(16) if not (mask >> x & 1))[:4]
    require(len(absent) == 4, "four absent points required")
    differences = tuple(x ^ absent[0] for x in absent[1:])
    normal = next(n for n in range(1, 16)
                  if all((n & x).bit_count() % 2 == 0 for x in differences))
    value = (normal & absent[0]).bit_count() % 2
    half = sum(1 << x for x in range(16) if (normal & x).bit_count() % 2 != value)
    extra = mask & ~half
    require(half.bit_count() == 8 and extra.bit_count() <= 4, "affine cover invariant")
    return half, extra


def binary_rank(rows):
    require(len(rows) <= 16 and all(type(x) is int and 0 <= x < 32 for x in rows),
            "five-bit rank domain")
    basis = [0] * 5
    for row in rows:
        for bit in range(4, -1, -1):
            if not row >> bit & 1:
                continue
            if basis[bit]:
                row ^= basis[bit]
            else:
                basis[bit] = row
                break
    return sum(x != 0 for x in basis)


def hyperplanes():
    masks = tuple(sum(1 << x for x in range(16)
                      if (normal & x).bit_count() % 2 == value)
                  for normal in range(1, 16) for value in (0, 1))
    require(len(masks) == len(set(masks)) == 30, "affine hyperplane inventory")
    for half in masks:
        labels = tuple(1 | (x << 1) for x in range(16) if half >> x & 1)
        require(half.bit_count() == 8 and binary_rank(labels) == 4,
                "odd affine hyperplane has linear rank four")
    return masks


def exhaustive_transfer():
    """Check all 2^16 supports against the independent 30-hyperplane oracle."""
    planes = hyperplanes()
    histogram = Counter()
    admissible, failures, maximum = 0, 0, 0
    sharp = None
    for mask in range(1 << 16):
        size = mask.bit_count()
        minimum = min((mask & ~half).bit_count() for half in planes)
        histogram[size, minimum] += 1
        if size > 12:
            require(minimum > 4, "cardinality boundary must fail")
            continue
        admissible += 1
        half, extra = cover(mask)
        valid = half in planes and mask == (mask & half) | extra
        valid = valid and extra.bit_count() <= 4 and not extra & half
        failures += not valid
        maximum = max(maximum, extra.bit_count())
        if minimum == 4 and sharp is None:
            sharp = {"support": mask, "half": half, "extra": extra,
                     "minimum_extra": minimum}
    require(admissible == 64839 and failures == 0 and maximum == 4,
            "complete affine transfer coverage")
    require(sharp is not None and histogram[13, 5] == 560, "sharp boundary controls")
    return {"all_subsets": 65536, "admissible_subsets": admissible,
            "errors": failures, "hyperplanes": len(planes), "maximum_extra": maximum,
            "histogram": [[s, k, n] for (s, k), n in sorted(histogram.items())],
            "sharp_witness": sharp, "thirteen_point_controls": 560}


if __name__ == "__main__":
    result = exhaustive_transfer()
    print("PASS_AFFINE_COVER_TRANSFER subsets=64839 boundary_controls=560 errors=0")
