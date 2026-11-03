"""Read-only exact corroboration; output is a hash-bound JSON receipt."""

import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import density


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def literal_kernel(modulus, pair):
    """No projective arithmetic: evaluate every dot product directly."""
    a, b = pair
    mask = 0
    for x in range(modulus):
        for y in range(modulus):
            if (a * x + b * y) % modulus == 0:
                mask |= 1 << (x * modulus + y)
    return mask


def literal_classes(modulus):
    """Choose representatives by equality of complete literal kernel masks."""
    kernels = {}
    primitive_mask = 0
    for x in range(modulus):
        for y in range(modulus):
            if gcd(x, y, modulus) == 1:
                primitive_mask |= 1 << (x * modulus + y)
                mask = literal_kernel(modulus, (x, y))
                kernels.setdefault(mask, (x, y))
    return tuple(kernels.values()), tuple(kernels), primitive_mask


def check_subset(modulus, reps, kernels, primitive_mask, indices):
    demands = tuple(reps[i] for i in indices)
    blocked = 0
    for i in indices:
        blocked |= kernels[i]
    actual = density.projection_count(modulus, demands)
    expected = modulus**2 - blocked.bit_count()
    expected_primitive = primitive_mask.bit_count() - (blocked & primitive_mask).bit_count()
    require(actual["count"] == expected, "divisor count differs from literal dots")
    require(actual["primitive_count"] == expected_primitive,
            "primitive count differs from literal dots")
    witness = density.projection_witness(modulus, demands)
    require((witness is not None) == (expected > 0), "existence criterion differs")
    if witness is not None:
        x, y = witness
        require(gcd(x, y, modulus) == 1, "witness is not primitive")
        require(not (blocked >> (x * modulus + y)) & 1, "witness is blocked")
    return 1


def exhaustive_subsets():
    count = 0
    shapes = []
    for modulus in range(2, 10):
        reps, kernels, primitive_mask = literal_classes(modulus)
        require(len(reps) <= 12, "exhaustive subset budget exceeded")
        for bits in range(1 << len(reps)):
            indices = tuple(i for i in range(len(reps)) if bits >> i & 1)
            count += check_subset(modulus, reps, kernels, primitive_mask, indices)
        shapes.append({"modulus": modulus, "classes": len(reps),
                       "subsets": 1 << len(reps)})
    return count, shapes


def larger_shapes():
    count = 0
    shapes = []
    moduli = (10, 12, 15, 16, 18, 20, 21, 25, 27, 30, 32, 35, 36, 49, 60, 64)
    for modulus in moduli:
        reps, kernels, primitive_mask = literal_classes(modulus)
        all_indices = tuple(range(len(reps)))
        subsets = [(), all_indices]
        subsets.extend((i,) for i in range(len(reps)))
        subsets.extend(tuple(j for j in all_indices if j != i)
                       for i in range(len(reps)))
        subsets.extend(itertools.combinations(range(min(12, len(reps))), 2))
        for indices in subsets:
            count += check_subset(modulus, reps, kernels, primitive_mask, indices)
        shapes.append({"modulus": modulus, "classes": len(reps),
                       "subsets": len(subsets)})
    return count, shapes


def interface_fixtures():
    fixtures = []
    for modulus, demands in (
        (9, ((1, 0), (1, 3))),
        (9, ((1, 0), (0, 1))),
        (9, ((1, 0), (2, 3), (1, 3))),
        (15, ((1, 0), (1, 3), (1, 5))),
    ):
        result = density.projection_count(modulus, demands)
        literal = sum(all((a*x + b*y) % modulus for a, b in demands)
                      for x in range(modulus) for y in range(modulus))
        require(result["count"] == literal, "interface fixture count failed")
        transformed = tuple((-a, -b) for a, b in demands) + demands + demands
        require(density.projection_count(modulus, transformed) == result,
                "units, duplicates or negative coefficients changed the count")
        fixtures.append({"modulus": modulus, "demands": demands, **result})
    points = ((0, 0), (1, 0), (2, 3))
    injective = sum(len({(x*a+y*b) % 9 for a, b in points}) == len(points)
                    for x in range(9) for y in range(9))
    require(injective == fixtures[2]["count"] == 60, "three-point projection failed")
    return fixtures


def rejecting_controls():
    bad = (
        (True, ()), (1, ()), (65, ()), (9, None), (9, ((True, 0),)),
        (9, ((0, 0),)), (9, ((3, 0),)), (9, ((1,),)),
        (9, ((2**31+1, 0),)), (9, ((1, 0),)*257),
    )
    for modulus, demands in bad:
        for function in (density.projection_count, density.projection_witness):
            try:
                function(modulus, demands)
            except ValueError:
                continue
            raise RuntimeError("malformed domain was accepted")
    m = 9
    demands = ((1, 0), (1, 3))
    literal = sum(all((a*x+b*y) % m for a, b in demands)
                  for x in range(m) for y in range(m))
    top_only = m*m - 1 - len(density.units(m))*2
    distinct_field_lines = (m-1)*(m+1-len(demands))
    require(literal != top_only, "missing-divisor mutant survived")
    require(literal != distinct_field_lines, "prime-field intersection mutant survived")
    nonprimitive = sum((3*x) % 9 != 0 for x in range(9) for _ in range(9))
    require(nonprimitive != 9*8, "unrestricted nonprimitive extension survived")
    return {"invalid_calls": 2*len(bad), "false_formula_controls": 3}


def bound_sources():
    manifest_path = PACKAGE / "SOURCES.json"
    require(manifest_path.stat().st_size <= 1024*1024, "source manifest too large")
    manifest = json.loads(manifest_path.read_text())
    root = PACKAGE.parent.parent
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.stat().st_size <= 1024*1024, "source input too large")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "predecessor context bytes changed")
        result[row["path"]] = digest
    return result


def main():
    inputs = bound_sources()
    small_count, small_shapes = exhaustive_subsets()
    large_count, large_shapes = larger_shapes()
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "density.py", "verify.py")
    hashes = {}
    for name in files:
        path = PACKAGE / name
        require(path.stat().st_size <= 1024*1024, "package file too large")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {
        "status": "PASS_COMPOSITE_PROJECTION_DENSITY",
        "claim_type": "scoped proof with exact finite corroboration",
        "exhaustive_subset_comparisons": small_count,
        "larger_shape_comparisons": large_count,
        "small_shapes": small_shapes, "larger_shapes": large_shapes,
        "fixtures": interface_fixtures(), "controls": rejecting_controls(),
        "package_sha256": hashes, "input_sha256": inputs,
        "new_kappa_claimed": False,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
